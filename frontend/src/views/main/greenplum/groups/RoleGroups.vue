<template>
  <v-container fluid>
    <v-card
      class="ma-3 elevation-10"
      tile
      :height="800"
      :loading="lightLoading > 0 && loading <= 0"
    >
      <v-row
        v-if="loading > 0"
        class="fill-height ma-0"
        align-content="center"
        justify="center"
      >
        <v-col class="text-subtitle-1 text-center" cols="12"> Building graph... </v-col>
        <v-col cols="6">
          <v-progress-linear
            color="deep-purple accent-4"
            indeterminate
            rounded
            height="6"
          ></v-progress-linear>
        </v-col>
      </v-row>

      <v-row v-else class="ma-0">
        <v-col class="pa-0" style="height: 800px">
          <v-toolbar
            v-show="lightLoading <= 0"
            id="main-toolbar"
            dense
            floating
            absolute
            flat
          >
            <v-text-field
              hide-details
              prepend-icon="mdi-magnify"
              single-line
              v-model="search"
              :suffix="suffixForSearch"
              @keydown.enter.exact.prevent="focusNextNode"
              @keydown.enter.shift.exact.prevent="focusPrevNode"
              class="mr-0"
            ></v-text-field>
            <v-btn icon @click="fitAnimated()">
              <v-icon>mdi-crosshairs-gps</v-icon>
            </v-btn>
            <v-btn icon @click="updateGraph()">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon v-bind="attrs" v-on="on">
                  <v-icon>mdi-information-outline</v-icon>
                </v-btn>
              </template>
              <strong>Search</strong>
              <div><v-chip x-small>Enter</v-chip> — move to next match</div>
              <div><v-chip x-small>Shift + Enter</v-chip> — move to previous match</div>
              <strong>Selection</strong>
              <div><v-chip x-small>Click</v-chip> — select one role or relation</div>
              <div>
                <v-chip x-small>Ctrl + Click</v-chip>
                — select multiple roles or relations
              </div>
            </v-tooltip>
          </v-toolbar>

          <network
            ref="network"
            :nodes="nodes"
            :edges="edges"
            :options="options"
            class="fill-height"
            @select="selectGraphElement"
            @drag-start="selectGraphElement"
          />
        </v-col>

        <v-divider vertical class="hidden-sm-and-down"></v-divider>

        <v-col cols="3" class="hidden-sm-and-down">
          <v-sheet height="775" class="overflow-auto">
            <action-edge-selected
              :selectedItems="selectedEdgesLabels"
              @update-graph="updateGraph()"
            />

            <action-node-selected
              :selectedItems="selectedNodes"
              @update-graph="updateGraph()"
            />

            <v-list
              v-if="!(selectedNodes.length > 0) && !(selectedEdges.length > 0)"
              subheader
              two-line
            >
              <v-subheader>Common Controls</v-subheader>

              <v-list-item @click="routeAddRole" :disabled="!hasAdminAccess">
                <v-list-item-content>
                  <v-list-item-title>Create Role</v-list-item-title>
                  <v-list-item-subtitle>
                    Go to the interface for adding roles
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>

              <v-list-item @click="routeAdminRoles">
                <v-list-item-content>
                  <v-list-item-title>Manage Roles</v-list-item-title>
                  <v-list-item-subtitle>
                    Go to the interface with the list of roles
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-sheet>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch, Ref } from "vue-property-decorator";
import { IVisNode, IVisEdge } from "@/interfaces/vue-models";
import { mainStore, roleStore } from "@/store";
import ActionNodeSelected from "./actions/NodeSelected.vue";
import ActionEdgeSelected from "./actions/EdgeSelected.vue";
import { IRolesGraphEdge, IRolesGraphNode, IRoleProfile } from "@/interfaces/greenplum";
import _ from "lodash";

@Component({
  components: {
    ActionNodeSelected,
    ActionEdgeSelected,
  },
})
export default class RoleGroups extends Vue {
  @Ref()
  network!: any;

  default_node_color = {
    border: "#2B7CE9",
    background: "#D2E5FF",
    highlight: {
      border: "#2B7CE9",
      background: "#D2E5FF",
    },
  };

  options = {
    layout: {
      randomSeed: 34,
      improvedLayout: false,
    },
    interaction: {
      hoverConnectedEdges: false,
      multiselect: true,
      selectConnectedEdges: false,
    },
    nodes: {
      color: this.default_node_color,
    },
    physics: {
      solver: "forceAtlas2Based",
      stabilization: {
        iterations: 4000,
      },
    },
    edges: {
      color: "lightgray",
      arrows: {
        to: {
          enabled: true,
        },
      },
    },
  };

  loading: number = 0;
  lightLoading: number = 0;
  search: string = "";
  focusNodeId: number | null = null;
  selectedNodes: IVisNode[] = [];
  selectedEdges: IVisEdge[] = [];
  findPosition: number = 0;
  firstLoad: boolean = true;

  nodes: IVisNode[] = [];
  edges: IVisEdge[] = [];

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  getVisNodes(graphNodes: IRolesGraphNode[], roles: IRoleProfile[]): IVisNode[] {
    return _.map(graphNodes, (node) => {
      return {
        id: node.oid,
        label: node.rolname,
        color: this.getCollorNode(node.oid, roles),
      };
    });
  }

  getVisEdges(graphEdges: IRolesGraphEdge[], roles: IRoleProfile[]): IVisEdge[] {
    return _.map(graphEdges, (edge) => {
      return {
        id: `${edge.from_oid}-${edge.to_oid}`,
        to: edge.to_oid,
        from: edge.from_oid,
        dashes: this.getDashesEdge(edge.to_oid, roles),
      };
    });
  }

  filterCondition(item: any, search: string): boolean {
    if (search) {
      return item ? item.toLowerCase().indexOf(search.toLowerCase()) != -1 : false;
    } else {
      return true;
    }
  }

  getCollorNode(oid: number, storage: IRoleProfile[]): any {
    const node = this.getRoleByOid(oid, storage);

    if (!node || node.rolcanlogin) {
      return this.default_node_color;
    }

    return {
      border: "darkred",
      background: "salmon",
      highlight: {
        border: "darkred",
        background: "salmon",
      },
    };
  }

  getDashesEdge(oid: number, storage: IRoleProfile[]): boolean {
    const node = this.getRoleByOid(oid, storage);
    return !node?.rolinherit;
  }

  getRoleByOid(oid: number, storage: IRoleProfile[]): IRoleProfile | undefined {
    return _.find(storage, { oid: oid });
  }

  getNodeById(id: number): IVisNode | undefined {
    return _.find(this.nodes, { id: id });
  }

  get suffixForSearch(): string {
    if (!this.search || !this.allFoundNodes.length) {
      return "";
    }
    return `${this.findPosition + 1} of ${this.allFoundNodes.length}`;
  }

  async updateStorage() {
    await Promise.all([roleStore.getRoles(), roleStore.getRolesGraph()]);
  }

  async updateItems() {
    let nodes: any = [];
    let edges: any = [];
    try {
      nodes = this.getVisNodes(roleStore.GraphNodes, roleStore.roles);
      edges = this.getVisEdges(roleStore.GraphEdges, roleStore.roles);
    } finally {
      this.nodes = nodes;
      this.edges = edges;
      this.selectGraphElement();
    }
  }

  async updateGraph() {
    ++this.lightLoading;
    try {
      await this.updateStorage();
      await this.updateItems();
    } finally {
      --this.lightLoading;
    }
  }

  async refresh() {
    ++this.loading;
    try {
      await this.updateGraph();
    } finally {
      --this.loading;
    }
  }

  onNodesUpdated() {
    if (this.network) {
      const nodes = this.network.getSelectedNodes();
      this.selectedNodes = this.nodes.filter((node) => nodes.includes(node.id));
    }
  }

  onEdgesUpdated() {
    if (this.network) {
      const edges = this.network.getSelectedEdges();
      this.selectedEdges = this.edges.filter((edge) => edges.includes(edge.id));
    }
  }

  selectGraphElement() {
    this.onNodesUpdated();
    this.onEdgesUpdated();
  }

  focusNextNode() {
    if (this.search) {
      this.findPosition += 1;
      if (this.findPosition >= this.allFoundNodes.length) {
        this.findPosition = 0;
      }
      const nodeId = this.foundSearchNodeId();
      if (nodeId) {
        this.focusAnimation(nodeId);
      }
    }
  }

  focusPrevNode() {
    if (this.search) {
      this.findPosition -= 1;
      if (this.findPosition < 0) {
        this.findPosition = this.allFoundNodes.length - 1;
      }
      const nodeId = this.foundSearchNodeId();
      if (nodeId) {
        this.focusAnimation(nodeId);
      }
    }
  }

  fitAnimated() {
    this.focusNodeId = null;

    this.network.fit({
      animation: {
        duration: 1000,
        easingFunction: "easeInOutQuad",
      },
    });
  }

  focusAnimation(nodeId: number) {
    this.focusNodeId = nodeId;

    this.network.focus(nodeId, {
      scale: 1.5,
      offset: { x: 0, y: 0 },
      animation: {
        duration: 800,
        easingFunction: "easeInOutQuad",
      },
    });
  }

  get allFoundNodes(): { id: number; len: any }[] {
    this.findPosition = 0;

    return _.chain(this.nodes)
      .filter((item) => this.filterCondition(item.label, this.search))
      .map((item) => {
        return {
          id: item.id,
          len: item.label.length,
        };
      })
      .sortBy("len")
      .value();
  }

  foundSearchNodeId(): number | undefined {
    const node = this.allFoundNodes[this.findPosition];
    return node?.id;
  }

  @Watch("search")
  focusNode(search: any) {
    if (!search) {
      this.fitAnimated();
    } else {
      const nodeId = this.foundSearchNodeId();
      if (nodeId && this.focusNodeId !== nodeId) {
        this.focusAnimation(nodeId);
      }
    }
  }

  get selectedEdgesLabels(): IVisEdge[] {
    return _.chain(this.selectedEdges)
      .map((item) => {
        const fromNode = this.getNodeById(item.from);
        const toNode = this.getNodeById(item.to);

        return {
          id: item.id,
          from: fromNode?.label,
          to: toNode?.label,
        };
      })
      .filter((item) => item.from && item.to)
      .value();
  }

  routeAdminRoles() {
    this.$router.push({
      name: "main-greenplum-roles",
    });
  }

  routeAddRole() {
    this.$router.push({
      name: "main-greenplum-roles-create",
    });
  }

  async activated() {
    if (this.firstLoad) {
      await this.refresh();
      this.firstLoad = false;
    } else {
      await this.updateGraph();
    }
  }
}
</script>

<style scoped>
#main-toolbar {
  background-color: rgba(255, 255, 255, 0.8);
}
</style>
