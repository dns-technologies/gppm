import { Store } from "vuex";
import { getModule } from "vuex-module-decorators";
import MainModule from "@/store/modules/main";
import AdminModule from "@/store/modules/admin";
import AclModule from "@/store/modules/acl";
import RoleModule from "@/store/modules/role";
import PermissionModule from "@/store/modules/permission";
import ResourceModule from "@/store/modules/resource";
import OwnerModule from "@/store/modules/owner";

let mainStore: MainModule;
let adminStore: AdminModule;
let aclStore: AclModule;
let roleStore: RoleModule;
let permissionStore: PermissionModule;
let resourceStore: ResourceModule;
let ownerStore: OwnerModule;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function initializeStores(store: Store<any>): void {
  mainStore = getModule(MainModule, store);
  adminStore = getModule(AdminModule, store);
  aclStore = getModule(AclModule, store);
  roleStore = getModule(RoleModule, store);
  permissionStore = getModule(PermissionModule, store);
  resourceStore = getModule(ResourceModule, store);
  ownerStore = getModule(OwnerModule, store);
}

export const modules = {
  main: MainModule,
  admin: AdminModule,
  acl: AclModule,
  role: RoleModule,
  permission: PermissionModule,
  resource: ResourceModule,
  owner: OwnerModule,
};

export {
  initializeStores,
  mainStore,
  adminStore,
  aclStore,
  roleStore,
  permissionStore,
  resourceStore,
  ownerStore,
};
