<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Manage Users</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn color="primary" :to="{ name: 'main-admin-users-create' }" class="mr-3">
          Create User
        </v-btn>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="users"
        :search="search"
        sort-by="email"
        :loading="loading > 0"
      >
        <template v-slot:item.is_active="{ item }">
          <v-icon v-if="item.is_active">mdi-check</v-icon>
        </template>

        <template v-slot:item.is_superuser="{ item }">
          <v-icon v-if="item.is_superuser">mdi-check</v-icon>
        </template>

        <template v-slot:top>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search User"
            single-line
            hide-details
            class="mx-4"
          >
          </v-text-field>

          <v-dialog v-model="dialogDelete" persistent max-width="450px">
            <v-card>
              <v-card-title class="text-h6 justify-center">
                Are you want to delete this user?
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
          <v-icon small @click="deleteItem(item)"> mdi-delete </v-icon>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { adminStore } from "@/store";
import { IUserProfile } from "@/interfaces/admin";

@Component
export default class AdminUsers extends Vue {
  editedItem!: IUserProfile;
  dialogDelete: boolean = false;
  search: string = "";
  loading: number = 0;

  headers = [
    {
      text: "Email",
      value: "email",
      align: "start",
    },
    { text: "Full Name", value: "full_name" },
    { text: "Is Active", value: "is_active" },
    { text: "Is Superuser", value: "is_superuser" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  get users(): IUserProfile[] {
    return adminStore.users;
  }

  async refresh() {
    ++this.loading;
    try {
      await adminStore.getUsers();
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }

  deleteItem(item: IUserProfile) {
    this.editedItem = Object.assign({}, item);
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    await adminStore.deleteUser(this.editedItem);
    await this.refresh();
  }

  editItem(item: IUserProfile) {
    this.$router.push({
      name: "main-admin-users-edit",
      params: {
        id: `${item.id}`,
      },
    });
  }

  closeDelete() {
    this.dialogDelete = false;
  }
}
</script>
