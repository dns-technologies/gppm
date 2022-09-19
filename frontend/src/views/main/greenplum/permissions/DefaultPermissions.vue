<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Default Permissons</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-row no-gutters>
        <v-col>
          <v-data-table
            :headers="headers"
            :items="items"
            sort-by="defaclacl.grantee"
            :loading="loading > 0"
          >
            <template v-slot:top>
              <v-row>
                <v-col>
                  <v-text-field
                    v-model="searchGrantee"
                    append-icon="mdi-magnify"
                    label="Search Grantee"
                    single-line
                    hide-details
                    class="ml-4"
                  >
                  </v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="searchGrantor"
                    append-icon="mdi-magnify"
                    label="Search Grantor"
                    single-line
                    hide-details
                  >
                  </v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="searchSchema"
                    append-icon="mdi-magnify"
                    label="Search Schema"
                    single-line
                    hide-details
                    class="mr-4"
                  >
                  </v-text-field>
                </v-col>
              </v-row>

              <v-dialog v-model="dialogDelete" persistent max-width="500px">
                <v-card>
                  <v-card-title class="text-h6 justify-center">
                    Are you want to delete this default permisson?
                  </v-card-title>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" text @click="closeDelete"
                      >Cancel</v-btn
                    >
                    <v-btn color="error darken-1" text @click="deleteItemConfirm"
                      >OK</v-btn
                    >
                    <v-spacer></v-spacer>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </template>

            <template v-slot:item.defaclacl="{ item }">
              <ul class="no-bullets">
                <li :key="index" v-for="(priv, index) in item.defaclacl.privs">
                  <v-icon> mdi-check </v-icon> {{ priv }}
                </li>
                <li :key="index" v-for="(privwgo, index) in item.defaclacl.privswgo">
                  <v-icon> mdi-check-all </v-icon> {{ privwgo }}
                </li>
              </ul>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-icon @click="deleteItem(item)" :disabled="!allowDelete(item)">
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </v-col>

        <v-divider vertical class="hidden-sm-and-down"></v-divider>

        <v-col cols="12" md="3">
          <v-container fluid>
            <v-combobox
              label="Database"
              clearable
              clear-icon="mdi-close-circle"
              prepend-icon="mdi-database"
              :items="databases"
              :value="selectedDatabase"
              :disabled="loading > 0"
              @input="changedDatabase"
            ></v-combobox>
          </v-container>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { aclStore, mainStore, permissionStore } from "@/store";
import {
  IAclDatabase,
  IAclDefaultPermission,
  IRevokeAllDefaults,
} from "@/interfaces/greenplum";
import _ from "lodash";

@Component
export default class DefaultPermissions extends Vue {
  headers = [
    { text: "Grantee", value: "defaclacl.grantee" },
    { text: "Grantor", value: "defaclacl.grantor" },
    { text: "Object Type", value: "objtype" },
    { text: "ACL Rule", value: "defaclacl", sortable: false },
    { text: "Schema", value: "schema", align: "start" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  loading: number = 0;
  searchGrantee: string = "";
  searchGrantor: string = "";
  searchSchema: string = "";

  selectedDatabase: any = null;
  dialogDelete: boolean = false;
  editedItem: IRevokeAllDefaults | null = null;
  databaseStore: IAclDatabase[] = [];
  rawItems: IAclDefaultPermission[] = [];

  get databases(): string[] {
    return _.map(this.databaseStore, "name");
  }

  deleteItem(item: any) {
    this.editedItem = {
      database: this.selectedDatabase,
      schema: item.schema,
      target_role: item.defaclacl.grantor,
      role_specification: item.defaclacl.grantee,
      entrie_type: item.objtype,
    };
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    if (this.editedItem) {
      await permissionStore.revokeDefaultPermissions(this.editedItem);
      await this.refresh();
    }
  }

  allowDelete(item: any): boolean {
    return Boolean(
      !item.defaclacl.public &&
        (mainStore.hasAdminAccess ||
          _.find(
            mainStore.currentAccess,
            (access) =>
              (access.type_of_entity === "Database" &&
                access.database === this.selectedDatabase) ||
              (access.type_of_entity === "Schema" &&
                access.database === this.selectedDatabase &&
                access.db_schema === item.schema),
          )),
    );
  }

  closeDelete() {
    this.dialogDelete = false;
  }

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  get itemsBeforeFiltered(): any[] {
    let results: any[] = [];

    this.rawItems.forEach((item) => {
      const one_item = item.defaclacl.map((acl) => {
        return {
          schema: item.schema,
          objtype: item.objtype,
          defaclacl: {
            grantor: acl.grantor,
            grantee: acl.grantee || "PUBLIC",
            privs: acl.privs,
            privswgo: acl.privswgo,
            public: !acl.grantee,
          },
        };
      });

      results.push(...one_item);
    });

    return results;
  }

  get items(): any[] {
    return this.itemsBeforeFiltered.filter(
      (item) =>
        this.filterCondition(item.schema, this.searchSchema) &&
        this.filterCondition(item.defaclacl.grantor, this.searchGrantor) &&
        this.filterCondition(item.defaclacl.grantee, this.searchGrantee),
    );
  }

  async updateStorage() {
    this.databaseStore = await aclStore.getDatabases();
  }

  async updateItems() {
    this.rawItems = await aclStore.getDefaultPermissions(this.selectedDatabase);
  }

  async changedDatabase(database: any) {
    ++this.loading;
    try {
      this.rawItems = [];
      this.selectedDatabase = database;
      await this.updateItems();
    } finally {
      --this.loading;
    }
  }

  async refresh() {
    ++this.loading;
    try {
      await this.updateStorage();
      await this.updateItems();
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }
}
</script>

<style>
ul.no-bullets {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
</style>
