<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-toolbar flat class="white--text indigo">
        <v-toolbar-title primary-title>
          <div class="text-h5">Role Members</div>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon :disabled="loading > 0" class="white--text" @click="refresh">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="items"
        sort-by="rolname"
        :loading="loading > 0"
      >
        <template v-slot:top>
          <v-row>
            <v-col>
              <v-text-field
                v-model="searchRole"
                append-icon="mdi-magnify"
                label="Search Role"
                single-line
                hide-details
                class="ml-4"
              >
              </v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="searchBelongsTo"
                append-icon="mdi-magnify"
                label="Search Belongs"
                single-line
                hide-details
              >
              </v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="searchMembersOf"
                append-icon="mdi-magnify"
                label="Search Members"
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
        </template>

        <template v-slot:item.belongs="{ item }">
          <v-chip-group active-class="primary--text" column>
            <div :key="index" v-for="(belong, index) in item.belongs">
              <v-chip v-if="item.parents.includes(belong)" color="primary" label small>
                {{ belong }}
              </v-chip>
              <v-chip label small v-else>
                {{ belong }}
              </v-chip>
            </div>
          </v-chip-group>
        </template>

        <template v-slot:item.members="{ item }">
          <v-chip-group active-class="primary--text" column>
            <div :key="index" v-for="(member, index) in item.members">
              <v-chip v-if="item.childs.includes(member)" color="primary" label small>
                {{ member }}
              </v-chip>
              <v-chip label small v-else>
                {{ member }}
              </v-chip>
            </div>
          </v-chip-group>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-icon @click="editItem(item)"> mdi-pencil </v-icon>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { roleStore } from "@/store";
import { IRoleProfile, IRolesGraphEdge, IRolesGraphNode } from "@/interfaces/greenplum";
import { Graph } from "@/utils/reachable-nodes";
import { IVueBelongsMembers } from "@/interfaces/vue-models";
import ResourceEditDialog from "./MembersEditDialog.vue";
import _ from "lodash";

@Component({
  components: {
    ResourceEditDialog,
  },
})
export default class RoleMembers extends Vue {
  headers = [
    {
      text: "Role",
      value: "rolname",
      align: "start",
    },
    { text: "Belong To Roles", value: "belongs", sortable: false },
    { text: "Members Of Role", value: "members", sortable: false },
    {
      text: "Actions",
      value: "actions",
      sortable: false,
    },
  ];

  loading: number = 0;
  searchRole: string = "";
  searchBelongsTo: string = "";
  searchMembersOf: string = "";
  dialog: boolean = false;
  editedItem: IVueBelongsMembers | null = null;

  graphEdges: IRolesGraphEdge[] = [];
  graphNodes: IRolesGraphNode[] = [];
  roles: IRoleProfile[] = [];

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

  get filledGraph(): Graph {
    const graph = new Graph();

    _.forEach(this.graphEdges, (edge) => {
      graph.addEdge(edge.from_oid, edge.to_oid);
    });

    return graph;
  }

  get filledReversedGraph(): Graph {
    const graph = new Graph();

    _.forEach(this.graphEdges, (edge) => {
      graph.addEdge(edge.to_oid, edge.from_oid);
    });

    return graph;
  }

  get membersOfNodes(): Object {
    return this.filledGraph.allReachableNodes();
  }

  get belongsToNodes(): Object {
    return this.filledReversedGraph.allReachableNodes();
  }

  get childsOfNodes(): Object {
    return this.filledGraph.childsList();
  }

  get parentToNodes(): Object {
    return this.filledReversedGraph.childsList();
  }

  editItem(item: IVueBelongsMembers) {
    this.editedItem = item;
    this.dialog = true;
  }

  createItem() {
    this.editedItem = null;
    this.dialog = true;
  }

  getRoleByOid(oid: number): IRoleProfile | undefined {
    return _.find(this.roles, { oid: oid });
  }

  getNodesByOid(oid: number, dependency: Object): string[] {
    const oidArray = dependency[oid];
    if (!oidArray) {
      return [];
    }

    const result: any = _.chain(oidArray)
      .map((oid) => this.getRoleByOid(oid))
      .filter(Boolean)
      .map((item) => item?.rolname)
      .value();

    return result;
  }

  get itemsBeforeFiltered(): IVueBelongsMembers[] {
    return this.graphNodes.map((item) => {
      return {
        oid: item.oid,
        rolname: item.rolname,
        belongs: this.getNodesByOid(item.oid, this.belongsToNodes),
        members: this.getNodesByOid(item.oid, this.membersOfNodes),
        parents: this.getNodesByOid(item.oid, this.parentToNodes),
        childs: this.getNodesByOid(item.oid, this.childsOfNodes),
      };
    });
  }

  get items(): IVueBelongsMembers[] {
    return this.itemsBeforeFiltered.filter(
      (item) =>
        this.filterCondition(item.rolname, this.searchRole) &&
        this.filterConditionContains(item.belongs, this.searchBelongsTo) &&
        this.filterConditionContains(item.members, this.searchMembersOf),
    );
  }

  async needRefresh(payload: any) {
    await roleStore.changeLinksOfRole(payload);
    this.refresh();
  }

  async updateStorage() {
    try {
      await Promise.all([roleStore.getRoles(), roleStore.getRolesGraph()]);
    } finally {
      this.roles = roleStore.roles;
      this.graphNodes = roleStore.GraphNodes;
      this.graphEdges = roleStore.GraphEdges;
    }
  }

  async refresh() {
    ++this.loading;
    try {
      await this.updateStorage();
    } finally {
      --this.loading;
    }
  }

  async activated() {
    await this.refresh();
  }
}
</script>

