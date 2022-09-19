import { api } from "@/api";
import router from "@/router";
import { AxiosError } from "axios";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import {
  IUserProfile,
  IUserProfileUpdate,
  IAppNotification,
  IContext,
  IAccess,
  IPublicAppInfo
} from "@/interfaces/admin";
import {
  getLocalContextId,
  getLocalToken,
  removeLocalContextId,
  removeLocalToken,
  saveLocalContextId,
  saveLocalToken
} from "@/utils/localstorage-helper";
import { UNAUTHORIZED } from "http-status-codes";
import _ from "lodash";

@Module({ name: "main" })
export default class MainModule extends VuexModule {
  token: string = "";
  contextId: number = 0;
  authType: string = "?"
  logInError: boolean = false;
  userProfile: IUserProfile = {
    email: "tmp@gppm.com",
    is_active: false,
    is_superuser: false,
    full_name: "",
    id: 0,
  };
  currentContext: IContext | null = null;
  dashboardMiniDrawer: boolean = false;
  dashboardShowDrawer: boolean = true;
  notifications: IAppNotification[] = [];
  currentAccess: IAccess[] = [];
  loading: number = 0;
  vueIsLoading: boolean = true;

  get hasAdminAccess(): boolean {
    return this.userProfile.is_active && this.userProfile.is_superuser;
  }

  get isLoggedIn(): boolean {
    return this.userProfile.is_active;
  }

  get firstNotification(): IAppNotification | false {
    return this.notifications.length > 0 && this.notifications[0];
  }

  get isLoading(): boolean {
    return this.loading > 0;
  }

  get hasActiveContext(): boolean {
    return !!this.currentContext;
  }

  @Mutation
  setLoading(loading: boolean) {
    this.loading += loading ? 1 : -1;
  }

  @Mutation
  setToken(payload: string) {
    this.token = payload;
  }

  @Mutation
  setLogInError(payload: boolean) {
    this.logInError = payload;
  }

  @Mutation
  setUserProfile(payload: IUserProfile | null) {
    this.userProfile = payload !== null ? payload : {
      email: "tmp@gppm.com",
      is_active: false,
      is_superuser: false,
      full_name: "",
      id: 0,
    };
  }

  @Mutation
  setCurrentAccess(payload: IAccess[]) {
    this.currentAccess = _.filter(payload, (payload) => payload.is_active);
  }

  @Mutation
  setAuthType(payload: IPublicAppInfo) {
    this.authType = payload.auth_type;
  }

  @Mutation
  setContext(payload: IContext | null) {
    if (payload) {
      this.currentContext = payload;
      saveLocalContextId(`${payload.id}`);
      this.contextId = payload.id;
    } else {
      this.currentContext = null;
      removeLocalContextId();
      this.contextId = 0;
    }
  }

  @Mutation
  setVueIsLoading(payload: boolean) {
    this.vueIsLoading = payload;
  }

  @Mutation
  setDashboardMiniDrawer(payload: boolean) {
    this.dashboardMiniDrawer = payload;
  }

  @Mutation
  setDashboardShowDrawer(payload: boolean) {
    this.dashboardShowDrawer = payload;
  }

  @Mutation
  addNotification(payload: IAppNotification) {
    this.notifications.push(payload);
  }

  @Mutation
  removeNotification(payload: IAppNotification) {
    this.notifications = this.notifications.filter(
      (notification) => notification !== payload,
    );
  }

  @Action
  async setCurrentContext(payload: IContext | null) {
    this.setContext(payload);
  }

  @Action
  async loadAuthProvider() {
    let db_info: IPublicAppInfo = {
      project_name: "?",
      api_version: "?",
      auth_type: "?",
    };
    try {
      const resp = await api.getPublicAppInfo();
      if (resp) {
        db_info = resp.data;
      }
    } catch (error) {
      await this.checkApiError(error);
    } finally {
      this.setAuthType(db_info);
    }
  }

  @Action
  async loadCurrentAccess() {
    let access: IAccess[] = [];
    try {
      if (this.contextId) {
        const responce = await api.getCurrentAccess(this.token, this.contextId);
        if (responce) {
          access = responce.data;
        }
      }
    } catch (error) {
      await this.checkApiError(error);
    } finally {
      this.setCurrentAccess(access);
    }
  }

  @Action
  async loadDefaultContext(payload: IContext[]) {
    let context: IContext | null = this.currentContext;

    try {
      let localContextId: any = context?.id;
      if (localContextId === undefined) {
        localContextId = getLocalContextId();
      }

      const actives = payload.filter((ctx) => ctx.is_active);
      const selected = actives.filter((context) => context.id == localContextId);

      if (selected.length) {
        context = selected[0];
        return;
      }

      if (actives.length) {
        context = actives[0];
        return;
      }

      context = null;
    } finally {
      await this.setCurrentContext(context);
    }
  }

  @Action
  async logIn(payload: { username: string; password: string }) {
    try {
      const response = await api.logInGetToken(payload.username, payload.password);
      const token = response.data.access_token;
      if (token) {
        saveLocalToken(token);
        this.setToken(token);
        this.setLogInError(false);
        await this.getUserProfile();
        await this.routeLoggedIn();
        this.addNotification({ content: "Logged in", color: "success" });
      } else {
        await this.logOut();
      }
    } catch (error) {
      this.setLogInError(true);
      await this.logOut();
    }
  }

  @Action
  async getUserProfile(payload: boolean = true) {
    let data: IUserProfile | null = null;
    try {
      const response = await api.getMe(this.token);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      if (payload) {
        await this.checkApiError(error);
      }
    } finally {
      this.setUserProfile(data);
    }
  }

  @Action
  async updateUserProfile(payload: IUserProfileUpdate) {
    const loadingNotification = { content: "Updating profile", showProgress: true };
    this.addNotification(loadingNotification);

    try {
      const response = await api.updateMe(this.token, payload);
      this.setUserProfile(response.data);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Profile successfully updated",
        color: "success",
      });
    } catch (error) {
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Profile updated with errors",
        color: "warning",
      });
      await this.checkApiError(error);
    }
  }

  @Action
  async checkLoggedIn() {
    if (this.isLoggedIn) {
      return;
    }

    let token = this.token;
    if (!token) {
      const localToken = getLocalToken();
      if (localToken) {
        this.setToken(localToken);
        token = localToken;
      }
    }
    if (token) {
      try {
        const response = await api.getMe(token);
        this.setUserProfile(response.data);
      } catch (error) {
        await this.removeLogIn();
      }
    } else {
      await this.removeLogIn();
    }
  }

  @Action
  async removeLogIn() {
    removeLocalToken();
    this.setToken("");
    this.setUserProfile(null);
  }

  @Action
  async logOut() {
    await this.removeLogIn();
    await this.routeLogOut();
  }

  @Action
  async userLogOut() {
    await this.logOut();
    this.addNotification({ content: "Logged out", color: "success" });
  }

  @Action
  async routeLogOut() {
    if (router.currentRoute.path !== "/login") {
      router.push("/login");
    }
  }

  @Action
  async checkApiError(payload: any) {
    const err = payload as AxiosError;
    if (err.response && err.response.status === UNAUTHORIZED) {
      await this.logOut();
    }
  }

  @Action
  async routeLoggedIn() {
    if (router.currentRoute.path === "/login" || router.currentRoute.path === "/") {
      router.push("/main");
    }
  }

  @Action
  async removeNotificationDelayed(payload: {
    notification: IAppNotification;
    timeout: number;
  }) {
    return new Promise((resolve, _reject) => {
      setTimeout(() => {
        this.removeNotification(payload.notification);
        resolve(true);
      }, payload.timeout);
    });
  }
}
