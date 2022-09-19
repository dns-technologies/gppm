<template>
  <div id="edge-selected" v-if="selectedItems.length > 0">
    <template>
      <v-dialog v-model="dialogDelete" persistent :max-width="450">
        <v-card>
          <v-card-title class="text-h6 justify-center">
            Are you want to remove member?
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" @click="closeRemove" text> Cancel </v-btn>
            <v-btn color="error darken-1" @click="removeItemConfirm" text> OK </v-btn>
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>

    <v-list subheader two-line>
      <v-subheader>Member Controls</v-subheader>

      <v-list-item @click="removeMember(selectedItems)" :disabled="!hasEditAccess">
        <v-list-item-content>
          <v-list-item-title>Disconnect Members</v-list-item-title>
          <v-list-item-subtitle>
            Removes a member role from root role
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit } from "vue-property-decorator";
import { IVisEdge } from "@/interfaces/vue-models";
import { mainStore, roleStore } from "@/store";
import { IRoleRelationship } from "@/interfaces/greenplum";
import _ from "lodash";

@Component
export default class ActionEdgeSelected extends Vue {
  @Prop()
  selectedItems!: IVisEdge[];

  @Emit()
  async updateGraph() {}

  dialogDelete: boolean = false;
  editedItems!: IRoleRelationship[];

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
      this.selectedItems,
      (edge) => !_.find(allRoles, { role: edge.from }),
    );

    return !withoutAccess;
  }

  removeMember(items: IVisEdge[]) {
    this.editedItems = _.map(items, (item) => {
      return {
        rolname: `${item.from}`,
        member: `${item.to}`,
      };
    });

    this.dialogDelete = true;
  }

  async removeItemConfirm() {
    this.closeRemove();
    await roleStore.removeMembersFromRole(this.editedItems);
    await this.updateGraph();
  }

  closeRemove() {
    this.dialogDelete = false;
  }
}
</script>
