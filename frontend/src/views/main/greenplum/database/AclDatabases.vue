<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title class="text-h5"> Manage Databases </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card :loading="loading > 0" tile flat min-height="4" />
      <v-row class="pa-3">
        <v-col cols="12" md="3">
          <v-text-field
            v-model="search"
            label="Filter Elements"
            flat
            solo
            outlined
            hide-details
            clearable
            dense
            clear-icon="mdi-close-circle"
            class="mb-3"
          ></v-text-field>
          <v-list height="650" class="overflow-auto">
            <template v-for="item in items">
              <v-list-item :key="item.name" @click="showPermissions(item)">
                <v-list-item-avatar>
                  <v-avatar :color="item.color" class="white--text">
                    {{ item.initials }}
                  </v-avatar>
                </v-list-item-avatar>

                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                </v-list-item-content>

                <v-list-item-action>
                  <v-btn depressed small @click.stop="goToSchemaPage(item.name)">
                    View
                    <v-icon color="orange darken-4" small right>
                      mdi-open-in-new
                    </v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </template>
          </v-list>
        </v-col>

        <v-divider vertical class="hidden-sm-and-down"></v-divider>

        <v-col>
          <div v-show="selectedItem">
            <acl-permissions
              :database="selectedItem"
              :loadingParrent="loading > 0"
              @need-refresh="refresh"
            />
          </div>

          <v-container fluid fill-height v-show="!selectedItem">
            <v-row justify="center">
              <div class="text-h6 font-weight-light grey--text">Select a Database</div>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>


<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { aclStore, roleStore } from "@/store";
import { IAclDatabase } from "@/interfaces/greenplum";
import { avatarCollorDatabase } from "@/utils/avatar-colorize";
import AclPermissions from "./AclPermissions.vue";
import { IVueAclCommon } from "@/interfaces/vue-models";
import _ from "lodash";

@Component({
  components: {
    AclPermissions,
  },
})
export default class AclDatabases extends Vue {
  selectedItem: IVueAclCommon | null = null;

  search: string = "";
  loading: number = 0;
  databaseStore: IAclDatabase[] = [];

  get rawItems(): any[] {
    return _.chain(this.databaseStore)
      .map((database) => {
        return {
          oid: database.oid,
          color: avatarCollorDatabase(database.name),
          name: `${database.name}`,
          acl: database.acl,
          initials: `${database.name[0].toUpperCase()}`,
        };
      })
      .value();
  }

  get items(): any[] {
    return _.filter(this.rawItems, (item) =>
      this.filterCondition(item.name, this.search),
    );
  }

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  showPermissions(item: any) {
    this.selectItem(item);
  }

  selectItem(item: IVueAclCommon | null) {
    if (!item) {
      this.selectedItem = null;
      return;
    }

    const db = aclStore.adminOneDatabase(item.oid, this.databaseStore);
    this.selectedItem = db
      ? {
          name: db.name,
          oid: db.oid,
          acl: db.acl,
          owner: db.owner,
        }
      : null;
  }

  goToSchemaPage(database: string) {
    this.$router.push({
      name: "main-greenplum-schemas",
      params: {
        connection: JSON.stringify({
          database,
          timestamp: Date.now(), // Для возбуждения изменений свойства компонента
        }),
      },
    });
  }

  async updateDatabases() {
    ++this.loading;
    try {
      this.databaseStore = await aclStore.getDatabases();
      this.selectItem(this.selectedItem);
    } finally {
      --this.loading;
    }
  }

  async refresh() {
    ++this.loading;
    try {
      await Promise.all([this.updateDatabases(), roleStore.getRoles()]);
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }
}
</script>
