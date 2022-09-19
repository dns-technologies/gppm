<template>
  <div id="node-selected" v-if="selectedItems.length > 0">
    <template>
      <v-dialog v-model="dialogDelete" persistent :max-width="450">
        <v-card>
          <v-card-title class="text-h6 justify-center">
            Are you want to delete this role?
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" @click="closeDelete" text> Cancel </v-btn>
            <v-btn color="error darken-1" @click="deleteItemConfirm" text> OK </v-btn>
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>

    <v-list subheader two-line>
      <v-subheader>Role Controls</v-subheader>

      <v-list-item
        @click="deleteItem(selectedItems)"
        :disabled="!allowDelete(selectedItems)"
      >
        <v-list-item-content>
          <v-list-item-title>Delete Role</v-list-item-title>
          <v-list-item-subtitle>
            Remove selected role from GreenPlum
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        v-show="selectedItems.length <= 1"
        @click="routeEditRole(selectedItems)"
      >
        <v-list-item-content>
          <v-list-item-title>Edit Role</v-list-item-title>
          <v-list-item-subtitle>
            Go to the interface for editing selected role
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        v-show="selectedItems.length > 1"
        @click="connectMembers()"
        :disabled="groups.length == 0 || members.length == 0 || !hasEditAccess"
      >
        <v-list-item-content>
          <v-list-item-title>Connect Members</v-list-item-title>
          <v-list-item-subtitle>
            Transfers rights from one role to another
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <div v-show="selectedItems.length > 1">
      <v-list subheader one-line>
        <v-subheader>Groups</v-subheader>

        <draggable v-model="groups" group="members" style="min-height: 56px">
          <template v-for="item in groupsNodes">
            <v-list-item :key="item.id" class="move-pointer">
              <v-list-item-icon>
                <v-icon> mdi-label </v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ item.label }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </draggable>
      </v-list>

      <v-list subheader one-line>
        <v-subheader>Members</v-subheader>

        <draggable v-model="members" group="members" style="min-height: 56px">
          <template v-for="item in membersNodes">
            <v-list-item :key="item.id" class="move-pointer">
              <v-list-item-icon>
                <v-icon> mdi-label </v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ item.label }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </draggable>
      </v-list>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit, Watch } from "vue-property-decorator";
import { IVisNode } from "@/interfaces/vue-models";
import { IRoleMember, IRoleRelationship } from "@/interfaces/greenplum";
import { mainStore, roleStore } from "@/store";
import draggable from "vuedraggable";
import _ from "lodash";

@Component({
  components: {
    draggable,
  },
})
export default class ActionNodeSelected extends Vue {
  @Prop()
  selectedItems!: IVisNode[];

  @Emit()
  async updateGraph() {}

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  get hasEditAccess(): boolean {
    if (mainStore.hasAdminAccess) {
      return true;
    }

    const allRoles = _.filter(mainStore.currentAccess, {
      type_of_entity: "Role",
    });

    if (!allRoles.length) {
      return false;
    }

    const withoutAccess = _.find(
      this.groupsNodes,
      (node) => !_.find(allRoles, { role: node.label }),
    );

    return !withoutAccess;
  }

  allowDelete(items: IVisNode[]): boolean {
    return (
      this.hasAdminAccess && !_.find(items, { label: mainStore.currentContext?.role })
    );
  }

  fillMembers(items: number[]) {
    let toAdd = _.chain(items)
      .difference(this.members)
      .difference(this.groups)
      .value();
    this.members = _.union(this.members, toAdd);
  }

  removeObsolete(items: number[]) {
    this.groups = _.intersection(this.groups, items);
    this.members = _.intersection(this.members, items);
  }

  @Watch("selectedItems")
  updateItems(items: IVisNode[]) {
    const itemsIds = _.map(items, "id");
    this.fillMembers(itemsIds);
    this.removeObsolete(itemsIds);
  }

  editedItems!: IRoleMember[];
  groups: number[] = [];
  members: number[] = [];
  dialogDelete: boolean = false;

  get groupsNodes(): IVisNode[] {
    const data: any = _.chain(this.groups)
      .map((group) => this.getNodeById(group))
      .filter(Boolean)
      .value();
    return data;
  }

  get membersNodes(): IVisNode[] {
    const data: any = _.chain(this.members)
      .map((member) => this.getNodeById(member))
      .filter(Boolean)
      .value();
    return data;
  }

  getNodeById(id: number): IVisNode | undefined {
    return _.find(this.selectedItems, { id: id });
  }

  deleteItem(items: IVisNode[]) {
    this.editedItems = _.map(items, (item) => {
      return {
        oid: item.id,
        rolname: item.label,
      };
    });

    this.dialogDelete = true;
  }

  async connectMembers() {
    const query: IRoleRelationship[] = [];

    _.forEach(this.groupsNodes, (group) =>
      _.forEach(this.membersNodes, (member) => {
        query.push({
          rolname: group.label,
          member: member.label,
        });
      }),
    );

    await roleStore.appendMembersToRole(query);
    await this.updateGraph();
  }

  async deleteItemConfirm() {
    this.closeDelete();
    await roleStore.deleteRoles(_.map(this.editedItems, "rolname"));
    await this.updateGraph();
  }

  closeDelete() {
    this.dialogDelete = false;
  }

  routeEditRole(item: IVisNode[]) {
    this.$router.push({
      name: "main-greenplum-roles-edit",
      params: {
        oid: `${item[0].id}`,
      },
    });
  }
}
</script>

<style scoped>
.move-pointer {
  cursor: move;
}
</style>
