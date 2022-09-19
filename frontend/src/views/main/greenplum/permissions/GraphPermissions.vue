<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Result Permissons</div>
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
            :search="searchGrantee"
            sort-by="grantee"
            :loading="loading > 0"
          >
            <template v-slot:top>
              <v-text-field
                v-model="searchGrantee"
                append-icon="mdi-magnify"
                label="Search Grantee"
                single-line
                hide-details
                class="mx-4"
              >
              </v-text-field>
            </template>

            <template v-slot:item.grantee="{ item }">
              <v-chip v-if="item.direct" color="primary" label>
                {{ item.grantee }}
              </v-chip>
              <v-chip label v-else>
                {{ item.grantee }}
              </v-chip>
            </template>

            <template v-slot:item.create="{ item }">
              <v-icon v-if="item.privs.create">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.create">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.connect="{ item }">
              <v-icon v-if="item.privs.connect">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.connect">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.temporary="{ item }">
              <v-icon v-if="item.privs.temporary">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.temporary">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.usage="{ item }">
              <v-icon v-if="item.privs.usage">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.usage">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.select="{ item }">
              <v-icon v-if="item.privs.select">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.select">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.insert="{ item }">
              <v-icon v-if="item.privs.insert">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.insert">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.update="{ item }">
              <v-icon v-if="item.privs.update">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.update">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.delete="{ item }">
              <v-icon v-if="item.privs.delete">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.delete">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.truncate="{ item }">
              <v-icon v-if="item.privs.truncate">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.truncate">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.references="{ item }">
              <v-icon v-if="item.privs.references">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.references">mdi-check-all</v-icon>
            </template>

            <template v-slot:item.trigger="{ item }">
              <v-icon v-if="item.privs.trigger">mdi-check</v-icon>
              <v-icon v-if="item.privswgo.trigger">mdi-check-all</v-icon>
            </template>

            <template v-slot:footer.prepend>
              <div class="ml-2 hidden-sm-and-down">
                <div v-show="owner">
                  Owner: <strong>{{ owner | rereplaceSpaces }}</strong>
                </div>
                <div v-show="shared !== null">
                  Public: <strong>{{ shared ? "exist" : "absent" }}</strong>
                </div>
              </div>
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
            <v-combobox
              label="Schema"
              clearable
              clear-icon="mdi-close-circle"
              prepend-icon="mdi-tab"
              :items="schemas"
              :value="selectedSchema"
              :disabled="loading > 0 || !selectedDatabase"
              @input="changedSchema"
            ></v-combobox>
            <v-combobox
              label="Table"
              clearable
              clear-icon="mdi-close-circle"
              prepend-icon="mdi-table"
              :items="tables"
              :value="selectedTable"
              :disabled="loading > 0 || !selectedDatabase || !selectedSchema"
              @input="changedTable"
            ></v-combobox>
          </v-container>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { aclStore, permissionStore } from "@/store";
import {
  IAclDatabase,
  IAclSchema,
  IAclTable,
  IPermission,
} from "@/interfaces/greenplum";
import _ from "lodash";

@Component({
  filters: {
    rereplaceSpaces(name: string): string {
      if (name?.trim() === "") {
        return name.replace(/\s/g, "•");
      }
      return name;
    },
  },
})
export default class ResultPermissions extends Vue {
  get headers() {
    let addition_header: any[] = [];

    if (this.selectedDatabase) {
      if (this.selectedSchema) {
        if (this.selectedTable) {
          addition_header = [
            { text: "Select", value: "select" },
            { text: "Insert", value: "insert" },
            { text: "Update", value: "update" },
            { text: "Delete", value: "delete" },
            { text: "Truncate", value: "truncate" },
            { text: "References", value: "references" },
            { text: "Trigger", value: "trigger" },
          ];
        } else {
          addition_header = [
            { text: "Usage", value: "usage" },
            { text: "Create", value: "create" },
          ];
        }
      } else {
        addition_header = [
          { text: "Create", value: "create" },
          { text: "Temporary", value: "temporary" },
          { text: "Connect", value: "connect" },
        ];
      }
    }

    return [{ text: "Grantee", value: "grantee", align: "start" }, ...addition_header];
  }

  loading: number = 0;
  searchGrantee: string = "";

  selectedDatabase: any = null;
  selectedSchema: any = null;
  selectedTable: any = null;

  databaseStore: IAclDatabase[] = [];
  schemaStore: IAclSchema[] = [];
  tableStore: IAclTable[] = [];

  owner: string = "";
  shared: boolean | null = null;
  items: any[] = [];

  get databases(): string[] {
    return _.map(this.databaseStore, "name");
  }

  get schemas(): string[] {
    return _.map(this.schemaStore, "name");
  }

  get tables(): string[] {
    return _.map(this.tableStore, "name");
  }

  async updateRulesDatabase(
    database: any,
    store: IAclDatabase[],
    payload: IPermission[],
  ): Promise<{
    owner: string;
    shared: boolean | null;
    acls: any[];
  }> {
    const { owner, shared, gratees } = await this.getGranteesFromStore(database, store);

    return {
      owner: owner,
      shared: shared,
      acls: payload.map((item) => {
        const all_privs = [...item.privs, ...item.privswgo];
        return {
          grantee: item.grantee || "PUBLIC",
          direct: gratees.includes(item.grantee),
          create: all_privs.includes("CREATE"),
          temporary: all_privs.includes("TEMPORARY"),
          connect: all_privs.includes("CONNECT"),
          privs: {
            create: item.privs.includes("CREATE"),
            temporary: item.privs.includes("TEMPORARY"),
            connect: item.privs.includes("CONNECT"),
          },
          privswgo: {
            create: item.privswgo.includes("CREATE"),
            temporary: item.privswgo.includes("TEMPORARY"),
            connect: item.privswgo.includes("CONNECT"),
          },
        };
      }),
    };
  }

  async updateRulesSchema(
    schema: any,
    store: IAclSchema[],
    payload: IPermission[],
  ): Promise<{
    owner: string;
    shared: boolean | null;
    acls: any[];
  }> {
    const { owner, shared, gratees } = await this.getGranteesFromStore(schema, store);

    return {
      owner: owner,
      shared: shared,
      acls: payload.map((item) => {
        const all_privs = [...item.privs, ...item.privswgo];
        return {
          grantee: item.grantee || "PUBLIC",
          direct: gratees.includes(item.grantee),
          usage: all_privs.includes("USAGE"),
          create: all_privs.includes("CREATE"),
          privs: {
            usage: item.privs.includes("USAGE"),
            create: item.privs.includes("CREATE"),
          },
          privswgo: {
            usage: item.privswgo.includes("USAGE"),
            create: item.privswgo.includes("CREATE"),
          },
        };
      }),
    };
  }

  async updateRulesTable(
    table: any,
    store: IAclTable[],
    payload: IPermission[],
  ): Promise<{
    owner: string;
    shared: boolean | null;
    acls: any[];
  }> {
    const { owner, shared, gratees } = await this.getGranteesFromStore(table, store);

    return {
      owner: owner,
      shared: shared,
      acls: payload.map((item) => {
        const all_privs = [...item.privs, ...item.privswgo];
        return {
          grantee: item.grantee || "PUBLIC",
          direct: gratees.includes(item.grantee),
          select: all_privs.includes("SELECT"),
          insert: all_privs.includes("INSERT"),
          update: all_privs.includes("UPDATE"),
          delete: all_privs.includes("DELETE"),
          truncate: all_privs.includes("TRUNCATE"),
          references: all_privs.includes("REFERENCES"),
          trigger: all_privs.includes("TRIGGER"),
          privs: {
            select: item.privs.includes("SELECT"),
            insert: item.privs.includes("INSERT"),
            update: item.privs.includes("UPDATE"),
            delete: item.privs.includes("DELETE"),
            truncate: item.privs.includes("TRUNCATE"),
            references: item.privs.includes("REFERENCES"),
            trigger: item.privs.includes("TRIGGER"),
          },
          privswgo: {
            select: item.privswgo.includes("SELECT"),
            insert: item.privswgo.includes("INSERT"),
            update: item.privswgo.includes("UPDATE"),
            delete: item.privswgo.includes("DELETE"),
            truncate: item.privswgo.includes("TRUNCATE"),
            references: item.privswgo.includes("REFERENCES"),
            trigger: item.privswgo.includes("TRIGGER"),
          },
        };
      }),
    };
  }

  cleanRows() {
    this.owner = "";
    this.shared = null;
    this.items = [];
  }

  setRows(payload: { owner: string; shared: boolean | null; acls: any[] }) {
    this.owner = payload.owner;
    this.shared = payload.shared;
    this.items = payload.acls;
  }

  async loadPermissions(): Promise<IPermission[]> {
    return aclStore.getGraphPermissions({
      database: this.selectedDatabase,
      schema: this.selectedSchema,
      table: this.selectedTable,
    });
  }

  async changedDatabase(database: any) {
    ++this.loading;
    try {
      this.cleanRows();
      this.selectedDatabase = database;
      this.selectedSchema = null;
      this.selectedTable = null;
      this.schemaStore = await aclStore.getSchemas(database);
      await this.updateItems();
    } finally {
      --this.loading;
    }
  }

  async changedSchema(schema: any) {
    ++this.loading;
    try {
      this.cleanRows();
      this.selectedSchema = schema;
      this.selectedTable = null;
      this.tableStore = await aclStore.getTables({
        database: this.selectedDatabase,
        schema: schema,
      });
      await this.updateItems();
    } finally {
      --this.loading;
    }
  }

  async changedTable(table: any) {
    ++this.loading;
    try {
      this.cleanRows();
      this.selectedTable = table;
      await this.updateItems();
    } finally {
      --this.loading;
    }
  }

  async updateStorage() {
    const data = await Promise.all([
      aclStore.getDatabases(),
      aclStore.getSchemas(this.selectedDatabase),
      aclStore.getTables({
        database: this.selectedDatabase,
        schema: this.selectedSchema,
      }),
    ]);
    this.databaseStore = data[0];
    this.schemaStore = data[1];
    this.tableStore = data[2];
  }

  async getGranteesFromStore(
    item: string,
    store: any,
  ): Promise<{ owner: string; shared: boolean | null; gratees: string[] }> {
    let owner: string = "";
    let shared: boolean | null = null;
    let gratees: string[] = [];
    try {
      const entity = _.find(store, { name: item });
      if (entity) {
        const permissions = await permissionStore.getPermissionByACLRule({
          acls: entity.acl,
        });
        owner = entity.owner;
        shared = !!_.find(permissions, { grantee: "" });
        gratees = _.map(permissions, "grantee");
      }
    } finally {
      return {
        owner,
        shared,
        gratees,
      };
    }
  }

  async updateItems() {
    let payload: {
      owner: string;
      shared: boolean | null;
      acls: any[];
    } = { owner: "", shared: null, acls: [] };

    try {
      if (this.selectedDatabase) {
        const permissions = await this.loadPermissions();
        if (this.selectedSchema) {
          if (this.selectedTable) {
            payload = await this.updateRulesTable(
              this.selectedTable,
              this.tableStore,
              permissions,
            );
          } else {
            payload = await this.updateRulesSchema(
              this.selectedSchema,
              this.schemaStore,
              permissions,
            );
          }
        } else {
          payload = await this.updateRulesDatabase(
            this.selectedDatabase,
            this.databaseStore,
            permissions,
          );
        }
      }
    } finally {
      this.setRows(payload);
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
