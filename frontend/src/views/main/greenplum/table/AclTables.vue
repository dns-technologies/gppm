<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title class="text-h5"> Manage Tables </v-toolbar-title>

        <v-spacer></v-spacer>

        <template>
          <div class="text-center">
            <v-menu :close-on-content-click="false" :nudge-width="250" offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn color="primary" v-bind="attrs" v-on="on" class="mr-3">
                  Connection
                </v-btn>
              </template>

              <v-card>
                <v-list>
                  <v-list-item>
                    <v-list-item-avatar>
                      <v-icon>mdi-database-settings</v-icon>
                    </v-list-item-avatar>

                    <v-list-item-content>
                      <v-list-item-title>Connection settings</v-list-item-title>
                      <v-list-item-subtitle>
                        Select base and schema from which to connect
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>

                <v-divider></v-divider>

                <v-list>
                  <v-list-item>
                    <v-combobox
                      label="Database"
                      :items="databases"
                      :value="selectedDatabase"
                      @input="changedDatabase"
                    >
                    </v-combobox>
                  </v-list-item>
                  <v-list-item>
                    <v-combobox
                      label="Schema"
                      :items="schemas"
                      :value="selectedSchema"
                      :disabled="!selectedDatabase"
                      @input="changedSchema"
                    >
                    </v-combobox>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-menu>
          </div>
        </template>

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
              </v-list-item>
            </template>
          </v-list>
        </v-col>

        <v-divider vertical class="hidden-sm-and-down"></v-divider>

        <v-col>
          <div v-show="selectedItem">
            <acl-permissions
              :database="selectedDatabase"
              :schema="selectedSchema"
              :table="selectedItem"
              :loadingParrent="loading > 0"
              @need-refresh="refresh"
            />
          </div>

          <v-container fluid fill-height v-show="!selectedItem">
            <v-row justify="center">
              <div class="text-h6 font-weight-light grey--text">Select a Table</div>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>


<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { aclStore, roleStore } from "@/store";
import { avatarCollorTable } from "@/utils/avatar-colorize";
import { IAclTable, IAclSchema, IAclDatabase } from "@/interfaces/greenplum";
import { IVueAclCommon } from "@/interfaces/vue-models";
import AclPermissions from "./AclPermissions.vue";
import _ from "lodash";

@Component({
  components: {
    AclPermissions,
  },
})
export default class AclTables extends Vue {
  @Prop()
  connection?: string;
  connectionProp?: string;

  loading: number = 0;
  selectedItem: IVueAclCommon | null = null;
  search: string = "";
  selectedDatabase: any = null;
  selectedSchema: any = null;
  databaseStore: IAclDatabase[] = [];
  schemaStore: IAclSchema[] = [];
  tableStore: IAclTable[] = [];

  get rawItems(): any[] {
    return _.chain(this.tableStore)
      .map((table) => {
        return {
          oid: table.oid,
          color: avatarCollorTable(table.name),
          name: `${table.name}`,
          acl: table.acl,
          initials: `${table.name[0].toUpperCase()}`,
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

  get databases(): string[] {
    return _.map(this.databaseStore, "name");
  }

  get schemas(): string[] {
    return _.map(this.schemaStore, "name");
  }

  async changedDatabase(database: any) {
    ++this.loading;
    try {
      this.selectedDatabase = database;
      this.schemaStore = await aclStore.getSchemas(database);
      this.selectedSchema = this.schemas[0];
      this.tableStore = await aclStore.getTables({
        database: this.selectedDatabase,
        schema: this.selectedSchema,
      });
      this.selectedItem = null;
    } finally {
      --this.loading;
    }
  }

  async changedSchema(schema: any) {
    ++this.loading;
    try {
      this.selectedSchema = schema;
      this.tableStore = await aclStore.getTables({
        database: this.selectedDatabase,
        schema: this.selectedSchema,
      });
      this.selectedItem = null;
    } finally {
      --this.loading;
    }
  }

  async setDefaultValues() {
    if (!this.selectedDatabase) {
      await this.changedDatabase(this.databases[0]);
    } else if (!this.selectedSchema) {
      await this.changedSchema(this.schemas[0]);
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

    const table = aclStore.adminOneTable(item.oid, this.tableStore);
    this.selectedItem = table
      ? {
          name: table.name,
          oid: table.oid,
          acl: table.acl,
          owner: table.owner,
        }
      : null;
  }

  async updateTables() {
    ++this.loading;
    try {
      if (this.connectionProp) {
        const { database, schema } = JSON.parse(this.connectionProp);
        this.connectionProp = undefined;
        await this.changedConnectonProp(database, schema);
      } else {
        await this.changedConnectonProp(
          this.selectedDatabase,
          this.selectedSchema,
          this.selectedItem,
        );
      }
      await this.setDefaultValues();
    } finally {
      --this.loading;
    }
  }

  async changedConnectonProp(database: any, schema: any, item: any = null) {
    this.selectedDatabase = database;
    this.selectedSchema = schema;
    const data = await Promise.all([
      aclStore.getDatabases(),
      aclStore.getSchemas(database),
      aclStore.getTables({
        database,
        schema,
      }),
    ]);
    this.databaseStore = data[0];
    this.schemaStore = data[1];
    this.tableStore = data[2];
    this.selectItem(item);
  }

  async refresh() {
    ++this.loading;
    try {
      await Promise.all([this.updateTables(), roleStore.getRoles()]);
    } finally {
      --this.loading;
    }
  }

  async activated() {
    this.connectionProp = this.connection;
    await this.refresh();
  }
}
</script>

