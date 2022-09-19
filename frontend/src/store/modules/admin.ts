import { api } from "@/api";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import {
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IContext,
  IContextCreate,
  IContextUpdate,
  IContextMini,
  IAccess,
  IAccessCreate,
  IAccessUpdate
} from "@/interfaces/admin";
import { mainStore } from "@/utils/store-accessor";
import _ from "lodash";

@Module({ name: "admin" })
export default class AdminModule extends VuexModule {
  users: IUserProfile[] = [];
  contexts: IContext[] = [];
  accesses: IAccess[] = [];

  get adminOneUser() {
    return (userId: number | null) => {
      const filteredUsers = this.users.filter((user) => user.id === userId);
      if (filteredUsers.length > 0) {
        return { ...filteredUsers[0] };
      } else {
        return null;
      }
    };
  }

  get adminOneContext() {
    return (contextId: number | null) => {
      const filteredContexts = this.contexts.filter((context) => context.id === contextId);
      if (filteredContexts.length > 0) {
        return { ...filteredContexts[0] };
      } else {
        return null;
      }
    };
  }

  get adminOneAccess() {
    return (accessId: number | null) => {
      const filteredAccesses = this.accesses.filter((access) => access.id === accessId);
      if (filteredAccesses.length > 0) {
        return { ...filteredAccesses[0] };
      } else {
        return null;
      }
    };
  }

  @Mutation
  setUsers(payload: IUserProfile[]) {
    this.users = _.sortBy(payload, "email");
  }

  @Mutation
  setContexts(payload: IContext[]) {
    this.contexts = _.sortBy(payload, "alias");
  }

  @Mutation
  setAccesses(payload: IAccess[]) {
    this.accesses = payload.filter((access) => access.context_id === mainStore.contextId);
  }

  @Action
  async getContexts() {
    let data: IContext[] = [];
    try {
      const response = await api.getContexts(mainStore.token);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setContexts(data);
    }
  }

  @Action
  async getContextsWithDefault(): Promise<boolean> {
    const beforeContext: IContext | null = _.cloneDeep(mainStore.currentContext);

    await this.getContexts();
    await mainStore.loadDefaultContext(this.contexts);

    const context = mainStore.currentContext;

    if (!_.isEqual(beforeContext, context)) {
      return !!context;
    } else {
      return false;
    }
  }

  @Action
  async getUsers() {
    let data: IUserProfile[] = [];
    try {
      const response = await api.getUsers(mainStore.token);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setUsers(data);
    }
  }

  @Action
  async getAccesses() {
    let data: IAccess[] = [];
    try {
      const response = await api.getAccesses(mainStore.token);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setAccesses(data);
    }
  }

  @Action
  async validateContext(payload: IContextMini): Promise<boolean> {
    let data: boolean = false;
    try {
      const response = await api.validateContext(mainStore.token, payload);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return data;
    }
  }

  @Action
  async createUser(payload: IUserProfileCreate) {
    const loadingNotification = { content: "Creating user", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.createUser(mainStore.token, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User successfully created",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User created with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async createContext(payload: IContextCreate) {
    const loadingNotification = { content: "Creating context", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.createContext(mainStore.token, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context successfully created",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context created with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async createAccess(payload: IAccessCreate) {
    const loadingNotification = { content: "Creating access", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.createAccess(mainStore.token, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access successfully created",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access created with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateUser(payload: { id: number; user: IUserProfileUpdate }) {
    const loadingNotification = { content: "Updating user", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateUser(mainStore.token, payload.id, payload.user);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateContext(payload: { id: number; context: IContextUpdate }) {
    const loadingNotification = { content: "Updating context", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateContext(mainStore.token, payload.id, payload.context);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateAccess(payload: { id: number; access: IAccessUpdate }) {
    const loadingNotification = { content: "Updating access", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateAccess(mainStore.token, payload.id, payload.access);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteUser(payload: IUserProfile) {
    const loadingNotification = { content: "Deleting user", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.deleteUser(mainStore.token, payload.id);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteContext(payload: IContext) {
    const loadingNotification = { content: "Deleting context", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.deleteContext(mainStore.token, payload.id);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Context deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteAccess(payload: IAccess) {
    const loadingNotification = { content: "Deleting access", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.deleteAccess(mainStore.token, payload.id);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Access deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }
}
