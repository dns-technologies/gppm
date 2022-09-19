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
    <template v-slot:item.usage="{ item }">
      <v-icon v-if="item.privs.usage">mdi-check</v-icon>
      <v-icon v-if="item.privswgo.usage">mdi-check-all</v-icon>
    </template>

    <template v-slot:item.create="{ item }">
      <v-icon v-if="item.privs.create">mdi-check</v-icon>
      <v-icon v-if="item.privswgo.create">mdi-check-all</v-icon>
    </template>

    <template v-slot:footer.prepend>
      <span v-if="schema" class="ml-2 hidden-sm-and-down">
        Schema: <strong>{{ schema.name | rereplaceSpaces }}</strong>
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
              label="Schema Owner"
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
  IGrantSchema,
  IGrantTablesInSchema,
  IPermission,
} from "@/interfaces/greenplum";
import { IVueAclCommon, IVueSchemaDetails } from "@/interfaces/vue-models";
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
export default class AclSchemaPermissions extends Vue {
  @Prop()
  schema!: IVueAclCommon;

  @Prop()
  database!: string;

  @Prop()
  loadingParrent!: boolean;

  @Emit()
  async needRefresh(payload: any = undefined) {
    if (!payload) {
      return;
    }

    const grant: IGrantSchema = {
      name: this.schema.name,
      role_specification: payload.grantee,
      with_grant_option: payload.grantOption,
      database: this.database,
      privileges: {
        create: payload.create,
        usage: payload.usage,
      },
    };

    await permissionStore.updatePermissionSchema(grant);
  }

  get hasEditAccess() {
    return (
      !this.loadingParrent &&
      Boolean(
        mainStore.hasAdminAccess ||
          _.find(
            mainStore.currentAccess,
            (access) =>
              (access.type_of_entity === "Database" &&
                access.database === this.database) ||
              (access.type_of_entity === "Schema" &&
                access.database === this.database &&
                access.db_schema === this.schema?.name),
          ),
      )
    );
  }

  async optionalEvents(payload: any) {
    const { grantee, optionName } = payload;

    let grant: IGrantTablesInSchema = {
      role_specification: grantee,
      with_grant_option: payload.grantOption,
      database: this.database,
      schema: this.schema.name,
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

    switch (optionName) {
      case "grant_select":
        grant.privileges.select = true;
        break;
      case "grant_all":
        grant.privileges = {
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
        // revoke_all
        break;
    }

    await permissionStore.updatePermissionTablesInSchema(grant);
  }

  optionalFields = [
    {
      name: "grant_select",
      title: "Grant SELECT to all tables",
      subtitle:
        "Grant SELECT privelege to all tables in schema, also sets DEFAULT privileges",
    },
    {
      name: "grant_all",
      title: "Grant ALL to all tables",
      subtitle:
        "Grant ALL of the available privileges to all tables in schema, also sets DEFAULT privileges",
    },
    {
      name: "revoke_all",
      title: "Revoke ALL from all tables",
      subtitle:
        "Revoke All of the available privileges from all tables in schema, also sets DEFAULT privileges",
    },
  ];

  headers = [
    {
      text: "Grantee",
      align: "start",
      value: "grantee",
    },
    { text: "Usage", value: "usage" },
    { text: "Create", value: "create" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  dialogFields = [
    {
      name: "usage",
      title: "Usage",
      subtitle: "Allows access to objects contained in the schema",
      value: true,
    },
    {
      name: "create",
      title: "Create",
      subtitle: "Allows new objects to be created within the schema",
      value: false,
    },
  ];

  loading: number = 0;
  search: string = "";
  itemsAcl: any[] = [];
  dialog: boolean = false;
  editedItem: IVueSchemaDetails | null = null;
  selectedRole: string = "";
  selectedRoleBefore: string = "";

  get items(): IVueSchemaDetails[] {
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
      type_of_entity: "schema",
      owner: this.selectedRole,
      database: this.database,
      schema: this.schema.name,
    });
    await this.needRefresh();
  }

  updateRules(payload: IPermission[]): any[] {
    return payload.map((item) => {
      const all_privs = [...item.privs, ...item.privswgo];

      return {
        grantee: item.grantee,
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
    });
  }

  editItem(item: IVueSchemaDetails) {
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
    await this.onSchemaChanges(this.schema);
  }

  @Watch("schema")
  async onSchemaChanges(payload?: IVueAclCommon) {
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

