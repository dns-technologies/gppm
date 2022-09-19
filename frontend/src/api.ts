import axios from "axios";
import { apiUrl } from "@/env";
import {
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IContext,
  IContextCreate,
  IContextUpdate,
  IContextMini,
  IAccessCreate,
  IAccessUpdate,
  IAccess,
  IPublicAppInfo
} from "./interfaces/admin";
import {
  IAclDatabase,
  IAclSchema,
  IAclTable,
  IRoleProfile,
  IRoleProfileCreate,
  IDecodeRulesRequest,
  IRolesGraph,
  IRoleMember,
  IRoleProfileUpdate,
  IGrantDatabase,
  IGrantSchemasInDatabase,
  IGrantSchema,
  IGrantTablesInSchema,
  IGrantTablesInDatabase,
  IGrantTable,
  IResourceGroup,
  IResourceGroupCreate,
  IResourceGroupUpdate,
  IResourceGroupAvailableLimits,
  IAclDefaultPermission,
  IRevokeAllDefaults,
  IUpdateEntityOwner,
  IPermission,
  IGraphPermissionParams,
} from "./interfaces/greenplum";

function auth(token: string, params: any = {}) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    params: params
  };
}

const apiGui = {
  // login
  async logInGetToken(username: string, password: string) {
    const params = new URLSearchParams([
      ["username", username],
      ["password", password]]
    );

    return axios.post(`${apiUrl}/api/v1/login/access-token`, params);
  },
  async getCurrentAccess(token: string, contextId: number) {
    return axios.get<IAccess[]>(`${apiUrl}/api/v1/users/my-accesses`, auth(token, { ctx: contextId }));
  },
  // users
  async getMe(token: string) {
    return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/me`, auth(token));
  },
  async updateMe(token: string, data: IUserProfileUpdate) {
    return axios.put<IUserProfile>(`${apiUrl}/api/v1/users/me`, data, auth(token),
    );
  },
  async getUsers(token: string) {
    return axios.get<IUserProfile[]>(`${apiUrl}/api/v1/users`, auth(token));
  },
  async createUser(token: string, data: IUserProfileCreate) {
    return axios.post(`${apiUrl}/api/v1/users`, data, auth(token));
  },
  async updateUser(token: string, userId: number, data: IUserProfileUpdate) {
    return axios.put(`${apiUrl}/api/v1/users/${userId}/one`, data, auth(token));
  },
  async deleteUser(token: string, userId: number) {
    return axios.delete(`${apiUrl}/api/v1/users/${userId}/one`, auth(token));
  },
  // contexts
  async getContexts(token: string) {
    return axios.get<IContext[]>(`${apiUrl}/api/v1/contexts`, auth(token));
  },
  async createContext(token: string, data: IContextCreate) {
    return axios.post(`${apiUrl}/api/v1/contexts`, data, auth(token));
  },
  async validateContext(token: string, data: IContextMini) {
    return axios.post(`${apiUrl}/api/v1/contexts/validate`, data, auth(token));
  },
  async updateContext(token: string, contextId: number, data: IContextUpdate) {
    return axios.put(`${apiUrl}/api/v1/contexts/${contextId}/one`, data, auth(token));
  },
  async deleteContext(token: string, contextId: number) {
    return axios.delete(`${apiUrl}/api/v1/contexts/${contextId}/one`, auth(token));
  },
  // accesses
  async getAccesses(token: string) {
    return axios.get<IAccess[]>(`${apiUrl}/api/v1/accesses`, auth(token));
  },
  async createAccess(token: string, data: IAccessCreate) {
    return axios.post(`${apiUrl}/api/v1/accesses`, data, auth(token));
  },
  async updateAccess(token: string, accessId: number, data: IAccessUpdate) {
    return axios.put(`${apiUrl}/api/v1/accesses/${accessId}/one`, data, auth(token));
  },
  async deleteAccess(token: string, accessId: number) {
    return axios.delete(`${apiUrl}/api/v1/accesses/${accessId}/one`, auth(token));
  },
}

const apiGreenPlum = {
  // acls
  async getAclDatabases(token: string, contextId: number) {
    return axios.get<IAclDatabase[]>(`${apiUrl}/api/v1/acls/databases`, auth(token, { ctx: contextId }));
  },
  async getAclSchemas(token: string, contextId: number, database: string) {
    return axios.get<IAclSchema[]>(`${apiUrl}/api/v1/acls/schemas`, auth(token, { ctx: contextId, db: database }));
  },
  async getAclTables(token: string, contextId: number, database: string, schema: string) {
    return axios.get<IAclTable[]>(`${apiUrl}/api/v1/acls/schemas/${schema}/tables`, auth(token, { ctx: contextId, db: database }));
  },
  // roles
  async getRoles(token: string, contextId: number) {
    return axios.get<IRoleProfile[]>(`${apiUrl}/api/v1/roles`, auth(token, { ctx: contextId }));
  },
  async updateRole(token: string, contextId: number, rolname: string, data: IRoleProfileUpdate) {
    return axios.put(`${apiUrl}/api/v1/roles/${rolname}/one`, data, auth(token, { ctx: contextId }));
  },
  async createRole(token: string, contextId: number, data: IRoleProfileCreate) {
    return axios.post(`${apiUrl}/api/v1/roles`, data, auth(token, { ctx: contextId }));
  },
  async deleteRole(token: string, contextId: number, rolname: string) {
    return axios.delete(`${apiUrl}/api/v1/roles/${rolname}/one`, auth(token, { ctx: contextId }));
  },
  async getRolesGraph(token: string, contextId: number) {
    return axios.get<IRolesGraph>(`${apiUrl}/api/v1/roles/graph`, auth(token, { ctx: contextId }));
  },
  async getMembersOfRole(token: string, contextId: number, rolname: string) {
    return axios.get<IRoleMember[]>(`${apiUrl}/api/v1/roles/${rolname}/members`, auth(token, { ctx: contextId }));
  },
  async removeMemberFromRole(token: string, contextId: number, rolname: string, member: string) {
    return axios.delete(`${apiUrl}/api/v1/roles/${rolname}/members/${member}/one`, auth(token, { ctx: contextId }));
  },
  async appendMemberToRole(token: string, contextId: number, rolname: string, member: string) {
    return axios.put(`${apiUrl}/api/v1/roles/${rolname}/members/${member}/one`, {}, auth(token, { ctx: contextId }));
  },
  // privileges
  async getPermissionByACLRule(_token: string, data: IDecodeRulesRequest) {
    return axios.post<IPermission[]>(`${apiUrl}/api/v1/privileges/decode/rules`, data);
  },
  async updatePermissionDatabase(token: string, contextId: number, data: IGrantDatabase) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/database`, data, auth(token, { ctx: contextId }));
  },
  async updatePermissionSchema(token: string, contextId: number, data: IGrantSchema) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/schema`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async updatePermissionSchemasInDatabase(token: string, contextId: number, data: IGrantSchemasInDatabase) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/schema/in-database`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async updatePermissionTablesInSchema(token: string, contextId: number, data: IGrantTablesInSchema) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/table/in-schema`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async updatePermissionTablesInDatabase(token: string, contextId: number, data: IGrantTablesInDatabase) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/table/in-database`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async updatePermissionTable(token: string, contextId: number, data: IGrantTable) {
    return axios.put(`${apiUrl}/api/v1/privileges/grant-on/table`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async getAclGraphPermissions(token: string, contextId: number, data: IGraphPermissionParams) {
    return axios.post<IPermission[]>(`${apiUrl}/api/v1/privileges/graph-permissions`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  async getAclDefaultPermissions(token: string, contextId: number, database: string) {
    return axios.get<IAclDefaultPermission[]>(`${apiUrl}/api/v1/privileges/default-permissions`, auth(token, { ctx: contextId, db: database }));
  },
  async revokeDefaultPermissions(token: string, contextId: number, data: IRevokeAllDefaults) {
    return axios.put(`${apiUrl}/api/v1/privileges/default-revoke-on/all`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  // resource-groups
  async getResourceGroups(token: string, contextId: number) {
    return axios.get<IResourceGroup[]>(`${apiUrl}/api/v1/resource-groups`, auth(token, { ctx: contextId }));
  },
  async createResourceGroup(token: string, contextId: number, data: IResourceGroupCreate) {
    return axios.post(`${apiUrl}/api/v1/resource-groups`, data, auth(token, { ctx: contextId }));
  },
  async updateResourceGroup(token: string, contextId: number, rsgname: string, data: IResourceGroupUpdate) {
    return axios.put(`${apiUrl}/api/v1/resource-groups/${rsgname}/one`, data, auth(token, { ctx: contextId }));
  },
  async deleteResourceGroup(token: string, contextId: number, rsgname: string) {
    return axios.delete(`${apiUrl}/api/v1/resource-groups/${rsgname}/one`, auth(token, { ctx: contextId }));
  },
  async getResourceGroupAvailableLimits(token: string, contextId: number) {
    return axios.get<IResourceGroupAvailableLimits>(`${apiUrl}/api/v1/resource-groups/available-limits`, auth(token, { ctx: contextId }));
  },
  // owners
  async updateOwner(token: string, contextId: number, data: IUpdateEntityOwner) {
    return axios.put(`${apiUrl}/api/v1/owners`, data, auth(token, { ctx: contextId, db: data.database }));
  },
  // utils
  async getPublicAppInfo() {
    return axios.get<IPublicAppInfo>(`${apiUrl}/api/v1/utils/public-app-info`);
  },
}

// All APIs
export const api = {
  ...apiGui,
  ...apiGreenPlum,
};
