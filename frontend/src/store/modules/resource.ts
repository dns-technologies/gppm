import { api } from "@/api";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import { IResourceGroup, IResourceGroupCreate, IResourceGroupUpdate, IResourceGroupAvailableLimits } from "@/interfaces/greenplum";
import { mainStore } from "@/utils/store-accessor";

@Module({ name: "resource" })
export default class ResourceModule extends VuexModule {
  resourceGroups: IResourceGroup[] = [];
  // Ограничение concurrency_max
  // На самомо деле максимально 262143
  // https://postgresqlco.nf/doc/en/param/max_connections/9.6/
  resourceGroupsLimits: IResourceGroupAvailableLimits = {
    concurrency_min: 0,
    concurrency_max: 250,
    cpu_rate_limit_min: 1,
    cpu_rate_limit_max: 100,
    memory_limit_min: 0,
    memory_limit_max: 100,
  };

  get adminOneResourceGroup() {
    return (resourceGroupId: number | null) => {
      const filteredRG = this.resourceGroups.filter((rg) => rg.oid === resourceGroupId);
      if (filteredRG.length > 0) {
        return { ...filteredRG[0] };
      } else {
        return null;
      }
    };
  }

  @Mutation
  setResourceGroups(payload: IResourceGroup[]) {
    this.resourceGroups = payload;
  }

  @Mutation
  setResourceGroupsLimits(payload: IResourceGroupAvailableLimits) {
    this.resourceGroupsLimits = payload;
  }

  @Action
  async getResourceGroupsLimits() {
    let data: IResourceGroupAvailableLimits = {
      concurrency_min: 0,
      concurrency_max: 250,
      cpu_rate_limit_min: 1,
      cpu_rate_limit_max: 100,
      memory_limit_min: 0,
      memory_limit_max: 100,
    };

    try {
      const response = await api.getResourceGroupAvailableLimits(mainStore.token, mainStore.contextId);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setResourceGroupsLimits(data);
    }
  }

  @Action
  async getResourceGroups() {
    let data: IResourceGroup[] = [];
    try {
      const response = await api.getResourceGroups(mainStore.token, mainStore.contextId);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setResourceGroups(data);
    }
  }

  @Action
  async createResourceGroup(payload: IResourceGroupCreate) {
    const loadingNotification = { content: "Creating resource group", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.createResourceGroup(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group successfully created",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group created with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateResourceGroup(payload: { rsgname: string; rsg: IResourceGroupUpdate }) {
    const loadingNotification = { content: "Updating resource group", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateResourceGroup(mainStore.token, mainStore.contextId, payload.rsgname, payload.rsg);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }


  @Action
  async deleteResourceGroup(payload: string) {
    const loadingNotification = { content: "Deleting resource group", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.deleteResourceGroup(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Resource group deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }
}