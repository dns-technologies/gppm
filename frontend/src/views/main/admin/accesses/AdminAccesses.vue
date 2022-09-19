<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Manage Accesses</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          class="mr-3"
          v-show="isContextSelected"
          @click="createItem"
        >
          Create Access
        </v-btn>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="accesses"
        sort-by="user"
        :loading="loading > 0"
      >
        <template v-slot:item.is_active="{ item }">
          <v-icon v-if="item.is_active">mdi-check</v-icon>
        </template>

        <template v-slot:top>
          <v-row>
            <v-col>
              <v-text-field
                v-model="searchUser"
                append-icon="mdi-magnify"
                label="Search User"
                single-line
                hide-details
                class="ml-4"
              >
              </v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="searchTypeOfEntity"
                append-icon="mdi-magnify"
                label="Search Type of Entity"
                single-line
                hide-details
              >
              </v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="searchEntity"
                append-icon="mdi-magnify"
                label="Search Entity"
                single-line
                hide-details
                class="mr-4"
              >
              </v-text-field>
            </v-col>
          </v-row>

          <v-dialog v-model="dialogDelete" persistent max-width="450px">
            <v-card>
              <v-card-title class="text-h6 justify-center">
                Are you want to delete this access?
              </v-card-title>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
                <v-btn color="error darken-1" text @click="deleteItemConfirm">OK</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <access-edit-dialog
            v-model="dialog"
            :edited-item="editedItem"
            u
            @need-refresh="needRefresh"
          />
        </template>

        <template v-slot:item.entity="{ item }">
          <v-chip class="mx-1" label v-show="item.role">
            {{ item.role }}
          </v-chip>
          <v-chip class="mx-1" label v-show="item.database">
            {{ item.database }}
          </v-chip>
          <v-chip class="mx-1" label v-show="item.db_schema">
            {{ item.db_schema }}
          </v-chip>
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
import { adminStore, mainStore } from "@/store";
import { IAccess, IUserProfile } from "@/interfaces/admin";
import AccessEditDialog from "./AccessEditDialog.vue";
import _ from "lodash";

@Component({
  components: {
    AccessEditDialog,
  },
})
export default class AdminAccess extends Vue {
  editedItem: IAccess | null = null;
  dialogDelete: boolean = false;
  searchUser: string = "";
  searchTypeOfEntity: string = "";
  searchEntity: string = "";
  dialog: boolean = false;
  loading: number = 0;

  headers = [
    {
      text: "User",
      value: "user",
      align: "start",
    },
    { text: "Type of Entity", value: "type_of_entity" },
    { text: "Entity", value: "entity", sortable: false },
    { text: "Is Active", value: "is_active" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  getUserById(id: number): IUserProfile | undefined {
    return _.find(adminStore.users, { id: id });
  }

  get rawAccesses(): any[] {
    return _.chain(adminStore.accesses)
      .map((access) => {
        const user = this.getUserById(access.user_id);
        return user
          ? {
              ...access,
              user: user?.email,
            }
          : null;
      })
      .filter(Boolean)
      .value();
  }

  get accesses(): any[] {
    return this.rawAccesses.filter(
      (item) =>
        this.filterCondition(item.user, this.searchUser) &&
        this.filterCondition(item.type_of_entity, this.searchTypeOfEntity) &&
        (this.filterCondition(item.role, this.searchEntity) ||
          this.filterCondition(item.database, this.searchEntity) ||
          this.filterCondition(item.db_schema, this.searchEntity)),
    );
  }

  get isContextSelected(): boolean {
    return !!mainStore.currentContext;
  }

  async needRefresh(payload: any) {
    const { method, data } = payload;

    const rg = {
      context_id: data.context_id,
      user_id: data.user_id,
      role: data.role,
      database: data.database,
      db_schema: data.db_schema,
      is_active: data.is_active,
    };

    if (method === "CREATE") {
      await adminStore.createAccess({
        ...rg,
      });
    } else {
      await adminStore.updateAccess({
        id: data.id,
        access: rg,
      });
    }

    this.refresh();
  }

  editItem(item: IAccess) {
    this.editedItem = item;
    this.dialog = true;
  }

  createItem() {
    this.editedItem = null;
    this.dialog = true;
  }

  async refresh() {
    ++this.loading;
    try {
      await Promise.all([adminStore.getUsers(), adminStore.getAccesses()]);
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }

  deleteItem(item: IAccess) {
    this.editedItem = Object.assign({}, item);
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    if (this.editedItem) {
      await adminStore.deleteAccess(this.editedItem);
      await this.refresh();
    }
  }

  closeDelete() {
    this.dialogDelete = false;
  }
}
</script>
