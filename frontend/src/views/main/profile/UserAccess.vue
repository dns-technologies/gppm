<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Manage Access</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-alert color="blue-grey" dark dense icon="mdi-school" class="ma-2">
        <span v-if="hasAdminAccess">
          You are an administrator. You have full rights without restrictions. The rules
          in the table don't apply to you.
        </span>
        <span v-else>
          You are a user. You are subject to editing restrictions. The rules apply only
          to the currently selected context.
        </span>
      </v-alert>

      <v-data-table
        :headers="headers"
        :items="accesses"
        sort-by="type_of_entity"
        :loading="loading > 0"
      >
        <template v-slot:item.is_active="{ item }">
          <v-icon v-if="item.is_active">mdi-check</v-icon>
        </template>

        <template v-slot:top>
          <v-row>
            <v-col>
              <v-text-field
                v-model="searchTypeOfEntity"
                append-icon="mdi-magnify"
                label="Search Type of Entity"
                single-line
                hide-details
                class="ml-4"
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
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mainStore } from "@/store";
import { IAccess } from "@/interfaces/admin";
import _ from "lodash";

@Component
export default class UserAccess extends Vue {
  searchTypeOfEntity: string = "";
  searchEntity: string = "";
  loading: number = 0;

  headers = [
    {
      text: "Type of Entity",
      value: "type_of_entity",
      align: "start",
    },
    { text: "Entity", value: "entity" },
  ];

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  get accesses(): IAccess[] {
    return _.filter(
      mainStore.currentAccess,
      (item) =>
        this.filterCondition(item.type_of_entity, this.searchTypeOfEntity) &&
        (this.filterCondition(item.role, this.searchEntity) ||
          this.filterCondition(item.database, this.searchEntity) ||
          this.filterCondition(item.db_schema, this.searchEntity)),
    );
  }

  async refresh() {
    ++this.loading;
    try {
      await mainStore.loadCurrentAccess();
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }
}
</script>
