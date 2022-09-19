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
      <span v-if="table" class="ml-2 hidden-sm-and-down">
        Table: <strong>{{ table.name | rereplaceSpaces }}</strong>
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
              label="Table Owner"
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
import { IGrantTable, IPermission } from "@/interfaces/greenplum";
import { IVueAclCommon, IVueTableDetails } from "@/interfaces/vue-models";
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
export default class AclTablePermissions extends Vue {
  @Prop()
  table!: IVueAclCommon;

  @Prop()
  database!: string;

  @Prop()
  schema!: string;

  @Prop()
  loadingParrent!: boolean;

  @Emit()
  async needRefresh(payload: any = undefined) {
    if (!payload) {
      return;
    }

    const grant: IGrantTable = {
      name: this.table.name,
      role_specification: payload.grantee,
      with_grant_option: payload.grantOption,
      database: this.database,
      schema: this.schema,
      privileges: {
        select: payload.select,
        insert: payload.insert,
        update: payload.update,
        delete: payload.delete,
        truncate: payload.truncate,
        references: payload.references,
        trigger: payload.trigger,
      },
    };

    await permissionStore.updatePermissionTable(grant);
  }

  get hasEditAccess(): boolean {
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
                access.db_schema === this.schema),
          ),
      )
    );
  }

  headers = [
    {
      text: "Grantee",
      align: "start",
      value: "grantee",
    },
    { text: "Select", value: "select" },
    { text: "Insert", value: "insert" },
    { text: "Update", value: "update" },
    { text: "Delete", value: "delete" },
    { text: "Truncate", value: "truncate" },
    { text: "References", value: "references" },
    { text: "Trigger", value: "trigger" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  dialogFields = [
    {
      name: "select",
      title: "Select",
      subtitle: "Allows SELECT from any column of a table",
      value: true,
    },
    {
      name: "insert",
      title: "Insert",
      subtitle: "Allows INSERT of a new row into a table",
      value: false,
    },
    {
      name: "update",
      title: "Update",
      subtitle: "Allows UPDATE of any column of a table",
      value: false,
    },
    {
      name: "delete",
      title: "Delete",
      subtitle: "Allows DELETE of a row from the specified table",
      value: false,
    },
    {
      name: "truncate",
      title: "Truncate",
      subtitle: "Allows TRUNCATE on a table",
      value: false,
    },
    {
      name: "references",
      title: "References",
      subtitle: "Allows creation of a foreign key constraint referencing a table",
      value: false,
    },
    {
      name: "trigger",
      title: "Trigger",
      subtitle: "Allows creation of a trigger on a table",
      value: false,
    },
  ];

  loading: number = 0;
  search: string = "";
  itemsAcl: any[] = [];
  dialog: boolean = false;
  editedItem: IVueTableDetails | null = null;
  selectedRole: string = "";
  selectedRoleBefore: string = "";

  get items(): IVueTableDetails[] {
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
      type_of_entity: "table",
      owner: this.selectedRole,
      database: this.database,
      schema: this.schema,
      table: this.table.name,
    });
    await this.needRefresh();
  }

  updateRules(payload: IPermission[]): any[] {
    return payload.map((item) => {
      const all_privs = [...item.privs, ...item.privswgo];

      return {
        grantee: item.grantee,
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
    });
  }

  editItem(item: IVueTableDetails) {
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

  async activated() {
    await this.onTableChanges(this.table);
  }

  @Watch("table")
  async onTableChanges(payload?: IVueAclCommon) {
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

