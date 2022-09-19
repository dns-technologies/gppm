import { api } from "@/api";
import { VuexModule, Module, Action } from "vuex-module-decorators";
import { mainStore } from "@/utils/store-accessor";
import {
  IUpdateEntityOwner,
} from "@/interfaces/greenplum";

@Module({ name: "owner" })
export default class OwnerModule extends VuexModule {
  @Action
  async updateEntityOwner(payload: IUpdateEntityOwner) {
    const loadingNotification = { content: "Changing owner", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateOwner(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Owner successfully changed",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Owner changed with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }
}
