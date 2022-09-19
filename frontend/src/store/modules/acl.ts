import { api } from "@/api";
import { VuexModule, Module, Action } from "vuex-module-decorators";
import { IAclDatabase, IAclDefaultPermission, IGraphPermissionParams, IAclSchema, IAclTable, IPermission } from "@/interfaces/greenplum";
import { mainStore } from "@/utils/store-accessor";
import _ from "lodash";

@Module({ name: "acl" })
export default class AclModule extends VuexModule {
  get adminOneDatabase() {
    return (databaseID: number | null, databases: IAclDatabase[] | null) => {
      if (databases) {
        const filteredDatabases = databases.filter((database) => database.oid === databaseID);
        if (filteredDatabases.length > 0) {
          return { ...filteredDatabases[0] };
        } else {
          return null;
        }
      } else {
        return null;
      }
    };
  }

  get adminOneShema() {
    return (schemaID: number | null, schemas: IAclSchema[] | null) => {
      if (schemas) {
        const filteredSchemas = schemas.filter((schema) => schema.oid === schemaID);
        if (filteredSchemas.length > 0) {
          return { ...filteredSchemas[0] };
        } else {
          return null;
        }
      } else {
        return null;
      }
    };
  }

  get adminOneTable() {
    return (tableID: number | null, tables: IAclTable[] | null) => {
      if (tables) {
        const filteredTables = tables.filter((table) => table.oid === tableID);
        if (filteredTables.length > 0) {
          return { ...filteredTables[0] };
        } else {
          return null;
        }
      } else {
        return null;
      }
    };
  }

  @Action
  async getDefaultPermissions(database: string | null): Promise<IAclDefaultPermission[]> {
    let data: IAclDefaultPermission[] = [];
    try {
      if (database) {
        const response = await api.getAclDefaultPermissions(mainStore.token, mainStore.contextId, database);
        if (response) {
          data = response.data;
        }
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return data;
    }
  }

  @Action
  async getGraphPermissions(payload: IGraphPermissionParams): Promise<IPermission[]> {
    let data: IPermission[] = [];
    try {
      if (payload.database) {
        const response = await api.getAclGraphPermissions(mainStore.token, mainStore.contextId, payload);
        if (response) {
          data = response.data;
        }
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return data;
    }
  }

  @Action
  async getDatabases(): Promise<IAclDatabase[]> {
    let data: IAclDatabase[] = [];
    try {
      const response = await api.getAclDatabases(mainStore.token, mainStore.contextId);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return _.sortBy(data, "name");
    }
  }

  @Action
  async getSchemas(database: string | null): Promise<IAclSchema[]> {
    let data: IAclSchema[] = [];
    try {
      if (database) {
        const response = await api.getAclSchemas(mainStore.token, mainStore.contextId, database);
        if (response) {
          data = response.data;
        }
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return _.sortBy(data, "name");
    }
  }

  @Action
  async getTables(payload: { database: string | null, schema: string | null }): Promise<IAclTable[]> {
    let data: IAclTable[] = [];
    try {
      if (payload.database && payload.schema) {
        const response = await api.getAclTables(mainStore.token, mainStore.contextId, payload.database, payload.schema);
        if (response) {
          data = response.data;
        }
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return _.sortBy(data, "name");
    }
  }
}
