<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title class="text-h5"> Manage Schemas </v-toolbar-title>

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
                        Select base from which to connect
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

          <v-virtual-scroll
            :key="timestamp"
            :items="items"
            height="650"
            item-height="56"
          >
            <template v-slot:default="{ item }">
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
                  <v-btn depressed small @click.stop="goToTablePage(item.name)">
                    View
                    <v-icon color="orange darken-4" small right>
                      mdi-open-in-new
                    </v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-col>

        <v-divider vertical class="hidden-sm-and-down"></v-divider>

        <v-col>
          <div v-show="selectedItem">
            <acl-permissions
              :database="selectedDatabase"
              :schema="selectedItem"
              :loadingParrent="loading > 0"
              @need-refresh="refresh"
            />
          </div>

          <v-container fluid fill-height v-show="!selectedItem">
            <v-row justify="center">
              <div class="text-h6 font-weight-light grey--text">Select a Schema</div>
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
import { avatarCollorSchema } from "@/utils/avatar-colorize";
import AclPermissions from "./AclPermissions.vue";
import { IAclDatabase, IAclSchema } from "@/interfaces/greenplum";
import { IVueAclCommon } from "@/interfaces/vue-models";
import _ from "lodash";

@Component({
  components: {
    AclPermissions,
  },
})
export default class AclSchemas extends Vue {
  @Prop()
  connection?: string;
  connectionProp?: string;

  timestamp: number = 0;
  loading: number = 0;
  selectedItem: IVueAclCommon | null = null;
  search: string = "";
  selectedDatabase: any = null;
  databaseStore: IAclDatabase[] = [];
  schemaStore: IAclSchema[] = [];

  get rawItems(): any[] {
    return _.chain(this.schemaStore)
      .map((schema) => {
        return {
          oid: schema.oid,
          color: avatarCollorSchema(schema.name),
          name: `${schema.name}`,
          acl: schema.acl,
          initials: `${schema.name[0].toUpperCase()}`,
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

  showPermissions(item: any) {
    this.selectItem(item);
  }

  async changedDatabase(database: any) {
    ++this.loading;
    try {
      this.selectedDatabase = database;
      this.schemaStore = await aclStore.getSchemas(database);
      this.selectedItem = null;
    } finally {
      --this.loading;
    }
  }

  async setDefaultValues() {
    if (!this.selectedDatabase) {
      await this.changedDatabase(this.databases[0]);
    }
  }

  selectItem(item: IVueAclCommon | null) {
    if (!item) {
      this.selectedItem = null;
      return;
    }

    const schema = aclStore.adminOneShema(item.oid, this.schemaStore);
    this.selectedItem = schema
      ? {
          name: schema.name,
          oid: schema.oid,
          acl: schema.acl,
          owner: schema.owner,
        }
      : null;
  }

  goToTablePage(schema: string) {
    this.$router.push({
      name: "main-greenplum-tables",
      params: {
        connection: JSON.stringify({
          database: this.selectedDatabase,
          schema,
          timestamp: Date.now(), // Для возбуждения изменений свойства компонента
        }),
      },
    });
  }

  async updateSchemas() {
    ++this.loading;
    try {
      if (this.connectionProp) {
        const { database } = JSON.parse(this.connectionProp);
        this.connectionProp = undefined;
        await this.changedConnectonProp(database);
      } else {
        await this.changedConnectonProp(this.selectedDatabase, this.selectedItem);
      }
      await this.setDefaultValues();
    } finally {
      --this.loading;
    }
  }

  async changedConnectonProp(database: any, item: any = null) {
    this.selectedDatabase = database;
    const data = await Promise.all([
      aclStore.getDatabases(),
      aclStore.getSchemas(database),
    ]);
    this.databaseStore = data[0];
    this.schemaStore = data[1];
    this.selectItem(item);
  }

  async refresh() {
    ++this.loading;
    try {
      await Promise.all([this.updateSchemas(), roleStore.getRoles()]);
    } finally {
      --this.loading;
    }
  }

  async activated() {
    this.timestamp = Date.now();
    this.connectionProp = this.connection;
    await this.refresh();
  }
}
</script>
