<template>
  <div>
    <v-app-bar dark color="primary" app fixed flat>
      <v-app-bar-nav-icon @click.stop="switchShowDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title v-text="appName" class="pl-4"></v-toolbar-title>
      <v-btn class="ml-4" icon to="/main/admin/contexts/create" v-show="hasAdminAccess">
        <v-icon>mdi-bookmark-plus</v-icon>
      </v-btn>
      <v-select
        :items="allContexts"
        :value="selectedContext"
        @change="changeContext"
        class="ml-4"
        flat
        chips
        hide-details
        item-text="alias"
        item-value="alias"
        return-object
        label="Select the desired context to activate it"
        solo-inverted
      >
        <template v-slot:no-data>
          <v-list-item>
            <v-list-item-title>
              No active context was found, <strong>create</strong> a new context or
              <strong>activate</strong> an existing one
            </v-list-item-title>
          </v-list-item>
        </template>
        <template v-slot:selection="{ attr, on, item, selected }">
          <v-chip
            v-bind="attr"
            :input-value="selected"
            color="indigo"
            class="white--text"
            v-on="on"
          >
            <v-icon left> mdi-bookmark </v-icon>
            <span v-text="item.alias"></span>
          </v-chip>
        </template>
        <template v-slot:item="{ item }">
          <v-list-item-avatar
            color="indigo"
            class="text-h5 font-weight-light white--text"
          >
            {{ item.alias.charAt(0) }}
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title v-text="item.alias"></v-list-item-title>
            <v-list-item-subtitle
              >{{ item.server }}:{{ item.port }}</v-list-item-subtitle
            >
          </v-list-item-content>
        </template>
      </v-select>
      <v-menu bottom left offset-y>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on" class="ml-4">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/main/profile">
            <v-list-item-content>
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-account</v-icon>
            </v-list-item-action>
          </v-list-item>
          <v-list-item @click="logout">
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-close</v-icon>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer
      v-model="showDrawer"
      persistent
      fixed
      app
      class="menu-subheader"
    >
      <v-list>
        <v-subheader>GUI Profile</v-subheader>
        <v-list-item to="/main/profile/view">
          <v-list-item-action>
            <v-icon>mdi-account</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>User Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-list v-show="hasAdminAccess" subheader>
        <v-divider></v-divider>
        <v-subheader>GUI Admin</v-subheader>
        <v-list-item to="/main/admin/contexts/all">
          <v-list-item-action>
            <v-icon>mdi-bookmark-multiple</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Contexts</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/admin/users/all">
          <v-list-item-action>
            <v-icon>mdi-account-multiple</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Users</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/admin/accesses/all">
          <v-list-item-action>
            <v-icon>mdi-account-switch</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Accesses</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <div v-show="contextSelected">
        <v-list subheader>
          <v-divider></v-divider>
          <v-subheader>GP Roles</v-subheader>
          <v-list-item to="/main/greenplum/roles/all">
            <v-list-item-action>
              <v-icon>mdi-account-group</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Manage Roles</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-show="hasAdminAccess" to="/main/greenplum/roles/create">
            <v-list-item-action>
              <v-icon>mdi-account-box</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Create Role</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/greenplum/roles/members">
            <v-list-item-action>
              <v-icon>mdi-account-network</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Role Members</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <v-list subheader>
          <v-divider></v-divider>
          <v-subheader>GP Groups</v-subheader>
          <v-list-item to="/main/greenplum/groups">
            <v-list-item-action>
              <v-icon>mdi-account-multiple-plus</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Role Groups</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/greenplum/resource-groups">
            <v-list-item-action>
              <v-icon>mdi-home-group</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Resource Groups</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <v-list subheader>
          <v-divider></v-divider>
          <v-subheader>GP Permissions</v-subheader>
          <v-list-item to="/main/greenplum/graph-permissions">
            <v-list-item-action>
              <v-icon>mdi-calendar</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Results</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/greenplum/default-permissions">
            <v-list-item-action>
              <v-icon>mdi-calendar-clock</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Defaults</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <v-list subheader>
          <v-divider></v-divider>
          <v-subheader>GP Entities</v-subheader>
          <v-list-item to="/main/greenplum/databases">
            <v-list-item-action>
              <v-icon>mdi-database</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Databases</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/greenplum/schemas">
            <v-list-item-action>
              <v-icon>mdi-tab</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Schemas</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/greenplum/tables">
            <v-list-item-action>
              <v-icon>mdi-table</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Tables</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </div>
    </v-navigation-drawer>

    <v-main>
      <v-progress-linear :indeterminate="loadingRoute"></v-progress-linear>
      <keep-alive>
        <router-view>
          <!--  Here is the view component that will be cached -->
        </router-view>
      </keep-alive>
    </v-main>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { appName } from "@/env";
import { mainStore, adminStore } from "@/store";
import { IContext } from "@/interfaces/admin";
import _ from "lodash";

@Component
export default class Main extends Vue {
  appName: string = appName;

  get loadingRoute(): boolean {
    return mainStore.isLoading;
  }

  get showDrawer(): boolean {
    return mainStore.dashboardShowDrawer;
  }

  set showDrawer(value: boolean) {
    mainStore.setDashboardShowDrawer(value);
  }

  switchShowDrawer() {
    mainStore.setDashboardShowDrawer(!mainStore.dashboardShowDrawer);
  }

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  async logout() {
    await mainStore.userLogOut();
  }

  get contextSelected(): boolean {
    return mainStore.currentContext !== null;
  }

  get selectedContext(): IContext | null {
    return mainStore.currentContext;
  }

  get allContexts(): IContext[] {
    return _.filter(adminStore.contexts, "is_active");
  }

  async changeContext(context: IContext | null) {
    await mainStore.setCurrentContext(context);
    // Ждем завершение анимации и перезагружаем
    setTimeout(() => {
      this.$router.go(0); // TODO: Найти более изящный выриант перезагрузки страницы
    }, 500);
  }
}
</script>

<style scoped>
.menu-subheader .v-subheader {
  height: 32px;
}
</style>
