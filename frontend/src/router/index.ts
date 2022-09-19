import Vue from "vue";
import VueRouter from "vue-router";

import RouterComponent from "@/components/RouterComponent.vue";

Vue.use(VueRouter);

export default new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      component: () => import(/* webpackChunkName: "start" */ "@/views/main/Start.vue"),
      children: [
        {
          path: "login",
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import(/* webpackChunkName: "login" */ "@/views/Login.vue"),
        },
        {
          path: "main",
          redirect: "main/profile",
          component: () =>
            import(/* webpackChunkName: "main" */ "@/views/main/Main.vue"),
          children: [
            {
              path: "greenplum",
              component: () =>
                import(
                  /* webpackChunkName: "main-greenplum" */ "@/views/main/greenplum/GreenPlum.vue"
                ),
              redirect: "greenplum/roles",
              children: [
                {
                  path: "databases",
                  name: "main-greenplum-databases",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-databases" */ "@/views/main/greenplum/database/AclDatabases.vue"
                    ),
                },
                {
                  path: "schemas",
                  name: "main-greenplum-schemas",
                  props: true,
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-schemas" */ "@/views/main/greenplum/schema/AclSchemas.vue"
                    ),
                },
                {
                  path: "tables",
                  name: "main-greenplum-tables",
                  props: true,
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-tables" */ "@/views/main/greenplum/table/AclTables.vue"
                    ),
                },
                {
                  path: "groups",
                  name: "main-greenplum-groups",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-groups" */ "@/views/main/greenplum/groups/RoleGroups.vue"
                    ),
                },
                {
                  path: "graph-permissions",
                  name: "main-greenplum-graph-permissions",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-graph-permissions" */ "@/views/main/greenplum/permissions/GraphPermissions.vue"
                    ),
                },
                {
                  path: "default-permissions",
                  name: "main-greenplum-default-permissions",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-default-permissions" */ "@/views/main/greenplum/permissions/DefaultPermissions.vue"
                    ),
                },
                {
                  path: "resource-groups",
                  name: "main-greenplum-resource-groups",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-greenplum-resource-groups" */ "@/views/main/greenplum/resources/ResourceGroups.vue"
                    ),
                },
                {
                  path: "roles",
                  component: RouterComponent,
                  redirect: "roles/all",
                  children: [
                    {
                      path: "all",
                      name: "main-greenplum-roles",
                      component: () =>
                        import(
                          /* webpackChunkName: "main-greenplum-roles" */ "@/views/main/greenplum/role/AdminRoles.vue"
                        ),
                    },
                    {
                      path: "create",
                      name: "main-greenplum-roles-create",
                      component: () =>
                        import(
                          /* webpackChunkName: "main-greenplum-roles-create" */ "@/views/main/greenplum/role/CreateRole.vue"
                        ),
                    },
                    {
                      path: "edit/:oid",
                      name: "main-greenplum-roles-edit",
                      component: () =>
                        import(
                          /* webpackChunkName: "main-greenplum-roles-edit" */ "@/views/main/greenplum/role/EditRole.vue"
                        ),
                    },
                    {
                      path: "members",
                      name: "main-greenplum-roles-members",
                      component: () =>
                        import(
                          /* webpackChunkName: "main-greenplum-roles-members" */ "@/views/main/greenplum/role/RoleMembers.vue"
                        ),
                    },
                  ],
                },
              ],
            },
            {
              path: "profile",
              component: () =>
                import(
                  /* webpackChunkName: "main-profile" */ "@/views/main/profile/Profile.vue"
                ),
              redirect: "profile/view",
              children: [
                {
                  path: "view",
                  name: "main-profile-user",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile-user" */ "@/views/main/profile/UserProfile.vue"
                    ),
                },
                {
                  path: "password",
                  name: "main-profile-password",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile-password" */ "@/views/main/profile/UserProfileEditPassword.vue"
                    ),
                },
                {
                  path: "access",
                  name: "main-profile-access",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile-access" */ "@/views/main/profile/UserAccess.vue"
                    ),
                },
              ],
            },
            {
              path: "admin",
              component: () =>
                import(
                  /* webpackChunkName: "main-admin" */ "@/views/main/admin/Admin.vue"
                ),
              redirect: "admin/users",
              children: [
                {
                  path: "users",
                  component: RouterComponent,
                  redirect: "users/all",
                  children: [
                    {
                      path: "all",
                      name: "main-admin-users",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-users" */ "@/views/main/admin/users/AdminUsers.vue"
                        ),
                    },
                    {
                      path: "edit/:id",
                      name: "main-admin-users-edit",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-users-edit" */ "@/views/main/admin/users/EditUser.vue"
                        ),
                    },
                    {
                      path: "create",
                      name: "main-admin-users-create",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-users-create" */ "@/views/main/admin/users/CreateUser.vue"
                        ),
                    },
                  ]
                },
                {
                  path: "contexts",
                  component: RouterComponent,
                  redirect: "contexts/all",
                  children: [
                    {
                      path: "all",
                      name: "main-admin-contexts",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-contexts" */ "@/views/main/admin/contexts/AdminContexts.vue"
                        ),
                    },
                    {
                      path: "edit/:id",
                      name: "main-admin-contexts-edit",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-contexts-edit" */ "@/views/main/admin/contexts/EditContext.vue"
                        ),
                    },
                    {
                      path: "create",
                      name: "main-admin-contexts-create",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-contexts-create" */ "@/views/main/admin/contexts/CreateContext.vue"
                        ),
                    },
                  ]
                },
                {
                  path: "accesses",
                  component: RouterComponent,
                  redirect: "accesses/all",
                  children: [
                    {
                      path: "all",
                      name: "main-admin-accesses",
                      component: () =>
                        import(
                            /* webpackChunkName: "main-admin-accesses" */ "@/views/main/admin/accesses/AdminAccesses.vue"
                        ),
                    },
                  ]
                }
              ]
            },
          ],
        },
      ],
    },
    {
      path: "/*",
      redirect: "/",
    },
  ],
});
