<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Manage Contexts</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          :to="{ name: 'main-admin-contexts-create' }"
          class="mr-3"
        >
          Create Context
        </v-btn>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="contexts"
        :search="search"
        sort-by="alias"
        :loading="loading > 0"
      >
        <template v-slot:item.is_active="{ item }">
          <v-icon v-if="item.is_active">mdi-check</v-icon>
        </template>

        <template v-slot:top>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search Context"
            single-line
            hide-details
            class="mx-4"
          >
          </v-text-field>

          <v-dialog v-model="dialogDelete" persistent max-width="450px">
            <v-card>
              <v-card-title class="text-h6 justify-center">
                Are you want to delete this context?
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
import { IContext } from "@/interfaces/admin";
import _ from "lodash";

@Component
export default class AdminContexts extends Vue {
  editedItem!: IContext;
  dialogDelete: boolean = false;
  search: string = "";
  loading: number = 0;

  headers = [
    {
      text: "Alias",
      value: "alias",
      align: "start",
    },
    { text: "Server", value: "server" },
    { text: "Port", value: "port" },
    { text: "Database", value: "database" },
    { text: "Role", value: "role" },
    { text: "Is Active", value: "is_active" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  get contexts(): IContext[] {
    return adminStore.contexts;
  }

  async refresh() {
    ++this.loading;
    try {
      const needRefresh = await adminStore.getContextsWithDefault();
      if (needRefresh) {
        this.refreshPage();
      }
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }

  deleteItem(item: IContext) {
    this.editedItem = Object.assign({}, item);
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    await adminStore.deleteContext(this.editedItem);
    await this.refresh();
  }

  editItem(item: IContext) {
    this.$router.push({
      name: "main-admin-contexts-edit",
      params: {
        id: `${item.id}`,
      },
    });
  }

  closeDelete() {
    this.dialogDelete = false;
  }

  refreshPage() {
    setTimeout(() => {
      this.$router.go(0);
    }, 500);
  }
}
</script>
