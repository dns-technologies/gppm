<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Manage Roles</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          :to="{ name: 'main-greenplum-roles-create' }"
          class="mr-3"
          v-show="hasAdminAccess"
        >
          Create Role
        </v-btn>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="users"
        :search="search"
        sort-by="rolname"
        :loading="loading > 0"
      >
        <template v-slot:item.rolcanlogin="{ item }">
          <v-icon v-if="item.rolcanlogin">mdi-check</v-icon>
        </template>

        <template v-slot:item.rolsuper="{ item }">
          <v-icon v-if="item.rolsuper">mdi-check</v-icon>
        </template>

        <template v-slot:item.rolcreaterole="{ item }">
          <v-icon v-if="item.rolcreaterole">mdi-check</v-icon>
        </template>

        <template v-slot:item.rolcreatedb="{ item }">
          <v-icon v-if="item.rolcreatedb">mdi-check</v-icon>
        </template>

        <template v-slot:item.rolinherit="{ item }">
          <v-icon v-if="item.rolinherit">mdi-check</v-icon>
        </template>

        <template v-slot:top>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search Role"
            single-line
            hide-details
            class="mx-4"
          >
          </v-text-field>

          <v-dialog v-model="dialogDelete" persistent max-width="450px">
            <v-card>
              <v-card-title class="text-h6 justify-center">
                Are you want to delete this role?
              </v-card-title>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
                <v-btn color="error darken-1" text @click="deleteItemConfirm">OK</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="editItem(item)"> mdi-pencil </v-icon>
          <v-icon small :disabled="!allowDelete(item)" @click="deleteItem(item)">
            mdi-delete
          </v-icon>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { IRoleMember, IRoleProfile } from "@/interfaces/greenplum";
import { mainStore, roleStore } from "@/store";

@Component
export default class AdminRoles extends Vue {
  editedItem!: IRoleMember;
  dialogDelete: boolean = false;
  search: string = "";
  loading: number = 0;

  headers = [
    {
      text: "Role Name",
      value: "rolname",
      align: "start",
    },
    { text: "Is Superuser", value: "rolsuper" },
    { text: "Is Create Role", value: "rolcreaterole" },
    { text: "Is Create Database", value: "rolcreatedb" },
    { text: "Is Inherit", value: "rolinherit" },
    { text: "Is Login", value: "rolcanlogin" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  get users(): IRoleProfile[] {
    return roleStore.roles;
  }

  async refresh() {
    ++this.loading;
    try {
      await roleStore.getRoles();
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }

  allowDelete(item: IRoleMember): boolean {
    return this.hasAdminAccess && item.rolname !== mainStore.currentContext?.role;
  }

  deleteItem(item: IRoleMember) {
    this.editedItem = Object.assign({}, item);
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    await roleStore.deleteRole(this.editedItem.rolname);
    await this.refresh();
  }

  editItem(item: IRoleMember) {
    this.$router.push({
      name: "main-greenplum-roles-edit",
      params: {
        oid: `${item.oid}`,
      },
    });
  }

  closeDelete() {
    this.dialogDelete = false;
  }
}
</script>
