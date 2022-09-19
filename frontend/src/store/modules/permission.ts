import { api } from "@/api";
import { VuexModule, Module, Action } from "vuex-module-decorators";
import { mainStore } from "@/utils/store-accessor";
import {
  IGrantDatabase,
  IPermission,
  IDecodeRulesRequest,
  IGrantSchema,
  IGrantTablesInSchema,
  IGrantTable,
  IRevokeAllDefaults,
  IGrantTablesInDatabase,
  IGrantSchemasInDatabase
} from "@/interfaces/greenplum";

@Module({ name: "permission" })
export default class PermissionModule extends VuexModule {
  @Action
  async getPermissionByACLRule(payload: IDecodeRulesRequest): Promise<IPermission[]> {
    let data: IPermission[] = [];
    try {
      const response = await api.getPermissionByACLRule(mainStore.token, payload);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
      throw error;
    } finally {
      return data;
    }
  }

  @Action
  async updatePermissionDatabase(payload: IGrantDatabase) {
    const loadingNotification = { content: "Updating permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionDatabase(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionSchemasAndTablesInDatabase(payload: { schema: IGrantSchemasInDatabase, table: IGrantTablesInDatabase }) {
    const loadingNotification = { content: "Updating included permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await Promise.all([
        api.updatePermissionSchemasInDatabase(mainStore.token, mainStore.contextId, payload.schema),
        api.updatePermissionTablesInDatabase(mainStore.token, mainStore.contextId, payload.table),
      ]);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionSchemasInDatabase(payload: IGrantSchemasInDatabase) {
    const loadingNotification = { content: "Updating included permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionSchemasInDatabase(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionSchema(payload: IGrantSchema) {
    const loadingNotification = { content: "Updating permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionSchema(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionTablesInDatabase(payload: IGrantTablesInDatabase) {
    const loadingNotification = { content: "Updating included permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionTablesInDatabase(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionTablesInSchema(payload: IGrantTablesInSchema) {
    const loadingNotification = { content: "Updating included permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionTablesInSchema(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Included permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updatePermissionTable(payload: IGrantTable) {
    const loadingNotification = { content: "Updating permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updatePermissionTable(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async revokeDefaultPermissions(payload: IRevokeAllDefaults) {
    const loadingNotification = { content: "Updating default permissions", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.revokeDefaultPermissions(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Default permissions successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Default permissions updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }
}
