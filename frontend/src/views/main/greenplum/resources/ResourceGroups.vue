<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Resource Groups</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn color="primary" @click="createItem" class="mr-3" v-show="hasAdminAccess">
          Create Resource Group
        </v-btn>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="resourceGroups"
        sort-by="name"
        item-key="name"
        :loading="loading > 0"
        single-expand
        show-expand
      >
        <template v-slot:top>
          <v-row>
            <v-col>
              <v-text-field
                v-model="searchGroup"
                append-icon="mdi-magnify"
                label="Search Resource Group"
                single-line
                hide-details
                class="ml-4"
              >
              </v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="searchRole"
                append-icon="mdi-magnify"
                label="Search Role In Group"
                single-line
                hide-details
                class="mr-4"
              >
              </v-text-field>
            </v-col>
          </v-row>

          <resource-edit-dialog
            v-model="dialog"
            :edited-item="editedItem"
            @need-refresh="needRefresh"
          />

          <v-dialog v-model="dialogDelete" persistent max-width="500px">
            <v-card>
              <v-card-title class="text-h6 justify-center">
                Are you want to delete this resource group?
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

        <template v-slot:expanded-item="{ headers, item }">
          <td :colspan="headers.length" class="pa-0">
            <v-simple-table dense>
              <template v-slot:default>
                <tbody>
                  <tr v-for="member in item.group_members" :key="member">
                    <td>{{ member }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </td>
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
import { mainStore, resourceStore } from "@/store";
import ResourceEditDialog from "./ResourceEditDialog.vue";
import { IResourceGroup } from "@/interfaces/greenplum";
import _ from "lodash";

@Component({
  components: {
    ResourceEditDialog,
  },
})
export default class ResourceGroups extends Vue {
  headers = [
    {
      text: "Group Name",
      value: "name",
      align: "start",
    },
    { text: "Concurrency", value: "concurrency" },
    { text: "CPU (%)", value: "cpu_rate_limit" },
    { text: "Memory (%)", value: "memory_limit" },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
    { text: "", value: "data-table-expand" },
  ];

  searchRole: string = "";
  searchGroup: string = "";
  dialog: boolean = false;
  editedItem: IResourceGroup | null = null;
  dialogDelete: boolean = false;
  loading: number = 0;

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  allowDelete(item: IResourceGroup): boolean {
    return (
      this.hasAdminAccess &&
      item.name !== "admin_group" &&
      item.name !== "default_group"
    );
  }

  deleteItem(item: IResourceGroup) {
    this.editedItem = Object.assign({}, item);
    this.dialogDelete = true;
  }

  async deleteItemConfirm() {
    this.closeDelete();
    if (this.editedItem) {
      await resourceStore.deleteResourceGroup(this.editedItem.name);
      await this.refresh();
    }
  }

  closeDelete() {
    this.dialogDelete = false;
  }

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  filterConditionContains(items: any[], search: string): boolean {
    if (search) {
      return Boolean(items.find((item) => this.filterCondition(item, search)));
    } else {
      return true;
    }
  }

  get rawResourceGroups(): IResourceGroup[] {
    return _.map(resourceStore.resourceGroups, (item) => {
      return {
        oid: item.oid,
        name: item.name,
        concurrency: item.concurrency,
        cpu_rate_limit: item.cpu_rate_limit,
        memory_limit: item.memory_limit,
        group_members: item.group_members,
      };
    });
  }

  get resourceGroups(): IResourceGroup[] {
    return _.filter(
      this.rawResourceGroups,
      (item) =>
        this.filterCondition(item.name, this.searchGroup) &&
        this.filterConditionContains(item.group_members, this.searchRole),
    );
  }

  async needRefresh(payload: any) {
    const { method, data } = payload;

    const rg = {
      cpu_rate_limit: data.cpu_rate_limit,
      concurrency: data.concurrency,
      memory_limit: data.memory_limit,
      group_members: data.group_members,
    };

    if (method === "CREATE") {
      await resourceStore.createResourceGroup({
        name: data.name,
        ...rg,
      });
    } else {
      await resourceStore.updateResourceGroup({
        rsgname: data.name,
        rsg: rg,
      });
    }

    this.refresh();
  }

  editItem(item: IResourceGroup) {
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
      await Promise.all([
        resourceStore.getResourceGroupsLimits(),
        resourceStore.getResourceGroups(),
      ]);
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }
}
</script>

<style scoped>
.theme--light.v-data-table {
  background-color: inherit;
}
</style>