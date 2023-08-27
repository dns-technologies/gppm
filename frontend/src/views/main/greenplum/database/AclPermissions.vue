<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :search="search"
    sort-by="grantee"
    class="elevation-0"
    :items-per-page="10"
    :footer-props="{
      disableItemsPerPage: true,
      itemsPerPageText: '',
    }"
    :loading="loading > 0"
  >
    <template v-slot:item.create="{ item }">
      <v-icon v-if="item.privs.create">mdi-check</v-icon>
      <v-icon v-if="item.privswgo.create">mdi-check-all</v-icon>
    </template>

    <template v-slot:item.temporary="{ item }">
      <v-icon v-if="item.privs.temporary">mdi-check</v-icon>
      <v-icon v-if="item.privswgo.temporary">mdi-check-all</v-icon>
    </template>

    <template v-slot:item.connect="{ item }">
      <v-icon v-if="item.privs.connect">mdi-check</v-icon>
      <v-icon v-if="item.privswgo.connect">mdi-check-all</v-icon>
    </template>

    <template v-slot:footer.prepend>
      <span v-if="database" class="ml-2 hidden-sm-and-down">
        Database: <strong>{{ database.name | rereplaceSpaces }}</strong>
      </span>
    </template>

    <template v-slot:top>
      <v-row no-gutters>
        <v-col cols="12" sm="6">
          <v-toolbar flat dense>
            <v-text-field
              v-model="search"
              label="Search Grantee"
              hide-details
              class="mr-4"
            >
            </v-text-field>
            <v-btn color="primary" @click="createItem" :disabled="!hasEditAccess">
              New Rule
            </v-btn>
          </v-toolbar>
        </v-col>

        <v-col>
          <v-toolbar flat dense>
            <v-combobox
              :items="roles"
              v-model="selectedRole"
              label="Database Owner"
              :disabled="!hasEditAccess"
              hide-details
              class="mr-4"
            ></v-combobox>
            <v-btn
              color="primary"
              @click="changeOwner"
              :disabled="!hasEditAccess || !roleChanged"
            >
              Change
            </v-btn>
          </v-toolbar>
        </v-col>
      </v-row>

      <acl-permission-dialog
        v-model="dialog"
        :edited-item="editedItem"
        :template="dialogFields"
        :optional-template="optionalFields"
        @optional-events="optionalEvents"
        @need-refresh="needRefresh"
      />
    </template>

    <template v-slot:item.actions="{ item }">
      <v-icon @click="editItem(item)" :disabled="!hasEditAccess || item.public">
        mdi-pencil
      </v-icon>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Vue, Prop, Watch, Emit } from "vue-property-decorator";
import {
  IGrantDatabase,
  IPermission,
  IGrantSchemasInDatabase,
  IGrantTablesInDatabase,
} from "@/interfaces/greenplum";
import { IVueAclCommon, IVueDatabaseDetails } from "@/interfaces/vue-models";
import { mainStore, ownerStore, permissionStore, roleStore } from "@/store";
import AclPermissionDialog from "@/components/AclPermissionDialog.vue";
import _ from "lodash";

@Component({
  components: {
    AclPermissionDialog,
  },
  filters: {
    rereplaceSpaces(name: string): string {
      if (name?.trim() === "") {
        return name.replace(/\s/g, "•");
      }
      return name;
    },
  },
})
export default class AclDatabasePermissions extends Vue {
  @Prop()
  database!: IVueAclCommon;

  @Prop()
  loadingParrent!: boolean;

  @Emit()
  async needRefresh(payload: any = undefined) {
    if (!payload) {
      return;
    }

    const grant: IGrantDatabase = {
      name: this.database.name,
      role_specification: payload.grantee,
      with_grant_option: payload.grantOption,
      privileges: {
        create: payload.create,
        temporary: payload.temporary,
        connect: payload.connect,
      },
    };

    await permissionStore.updatePermissionDatabase(grant);
  }

  get hasEditAccess(): boolean {
    return (
      !this.loadingParrent &&
      Boolean(
        mainStore.hasAdminAccess ||
          _.find(
            mainStore.currentAccess,
            (access) =>
              access.type_of_entity === "Database" &&
              access.database === this.database?.name,
          ),
      )
    );
  }

  async optionalEvents(payload: any) {
    const { grantee, grantOption, optionName } = payload;

    let tableGrant: IGrantTablesInDatabase = {
      role_specification: grantee,
      with_grant_option: grantOption,
      database: this.database.name,
      privileges: {
        select: false,
        insert: false,
        update: false,
        delete: false,
        truncate: false,
        references: false,
        trigger: false,
      },
    };

    let schemaGrant: IGrantSchemasInDatabase = {
      role_specification: grantee,
      with_grant_option: grantOption,
      database: this.database.name,
      privileges: {
        create: false,
        usage: false,
      },
    };

    switch (optionName) {
      case "grant_usage_schemas_select_tables":
        schemaGrant.privileges.usage = true;
        tableGrant.privileges.select = true;
        break;
      case "grant_usage_schemas_dml_tables":
        schemaGrant.privileges.usage = true;
        tableGrant.privileges = {
          select: true,
          insert: true,
          update: true,
          delete: true,
          truncate: false,
          references: false,
          trigger: false,
        };
        break;
      case "grant_all_schemas_all_tables":
        schemaGrant.privileges = {
          create: true,
          usage: true,
        };
        tableGrant.privileges = {
          select: true,
          insert: true,
          update: true,
          delete: true,
          truncate: true,
          references: true,
          trigger: true,
        };
        break;
      default:
        // revoke_all_schemas_all_tables
        break;
    }

    await permissionStore.updatePermissionSchemasAndTablesInDatabase({
      schema: schemaGrant,
      table: tableGrant,
    });
  }

  optionalFields = [
    {
      name: "grant_usage_schemas_select_tables",
      title: "Grant USAGE to all schemas and SELECT to all tables",
      subtitle:
        "Grant USAGE privilege to all schemas and SELECT privilege to all tables",
    },
    {
      name: "grant_usage_schemas_dml_tables",
      title: "Grant USAGE to all schemas and DML statements to all tables",
      subtitle:
        "Grant USAGE privilege to all schemas and SELECT, INSERT, UPDATE, DELETE privilege to all tables",
    },
    {
      name: "grant_all_schemas_all_tables",
      title: "Grant ALL to all schemas and ALL to all tables",
      subtitle: "Grant ALL of the available privileges to all schemas and tables",
    },
    {
      name: "revoke_all_schemas_all_tables",
      title: "Revoke ALL from all schemas and tables",
      subtitle: "Revoke ALL of the available privileges from all schemas and tables",
    },
  ];

  headers = [
    {
      text: "Grantee",
      align: "start",
      value: "grantee",
    },
    { text: "Create", value: "create" },
    { text: "Temporary", value: "temporary" },
    { text: "Connect", value: "connect" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  dialogFields = [
    {
      name: "create",
      title: "Create",
      subtitle: "Allows new schemas and publications to be created within the database",
      value: true,
    },
    {
      name: "temporary",
      title: "Temporary",
      subtitle: "Allows temporary tables to be created while using the database",
      value: false,
    },
    {
      name: "connect",
      title: "Connect",
      subtitle: "Allows the grantee to connect to the database",
      value: true,
    },
  ];

  loading: number = 0;
  search: string = "";
  itemsAcl: any[] = [];
  dialog: boolean = false;
  editedItem: IVueDatabaseDetails | null = null;
  selectedRole: string = "";
  selectedRoleBefore: string = "";

  get items(): IVueDatabaseDetails[] {
    return _.map(this.itemsAcl, (acl) => {
      return {
        ...acl,
        grantee: acl.grantee || "PUBLIC",
        public: !acl.grantee,
      };
    });
  }

  get roleChanged(): boolean {
    return !!this.selectedRole && this.selectedRole !== this.selectedRoleBefore;
  }

  async changeOwner() {
    await ownerStore.updateEntityOwner({
      type_of_entity: "database",
      owner: this.selectedRole,
      database: this.database.name,
    });
    await this.needRefresh();
  }

  updateRules(payload: IPermission[]): any[] {
    return payload.map((item) => {
      const all_privs = [...item.privs, ...item.privswgo];

      return {
        grantee: item.grantee,
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
    });
  }

  editItem(item: IVueDatabaseDetails) {
    this.editedItem = item;
    this.dialog = true;
  }

  createItem() {
    this.editedItem = null;
    this.dialog = true;
  }

  get roles(): string[] {
    return _.map(roleStore.roles, "rolname");
  }

  async mounted() {
    await this.onDatabaseChanges(this.database);
  }

  @Watch("database")
  async onDatabaseChanges(payload?: IVueAclCommon) {
    let items: any[] = [];
    let selectedRole = "";

    ++this.loading;
    try {
      if (payload) {
        selectedRole = payload.owner;
        items = this.updateRules(
          await permissionStore.getPermissionByACLRule({
            acls: payload.acl,
          }),
        );
      }
    } finally {
      this.selectedRoleBefore = selectedRole;
      this.selectedRole = selectedRole;
      this.itemsAcl = items;
      --this.loading;
    }
  }
}
</script>

