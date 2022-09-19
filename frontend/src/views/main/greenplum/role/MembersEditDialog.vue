<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="save" :class="{ 'no-click': loading }">
        <v-card>
          <v-card-title>
            <span class="text-h5">Edit Link</span>
          </v-card-title>

          <v-card-text>
            <validation-provider name="Role" rules="required_with_space">
              <v-text-field
                v-model="rolname"
                label="Role"
                hide-details
                outlined
                disabled
                class="pb-4"
              >
              </v-text-field>
            </validation-provider>

            <v-card>
              <v-tabs vertical>
                <v-tab>
                  <v-icon left>mdi-source-branch</v-icon>
                  Parents
                </v-tab>

                <v-tab>
                  <v-icon left>mdi-source-merge</v-icon>
                  Childs
                </v-tab>

                <v-tab-item>
                  <v-data-table
                    :headers="headers"
                    :items="parents"
                    class="elevation-0"
                    height="330"
                    hide-default-footer
                    disable-pagination
                    fixed-header
                  >
                    <template v-slot:top>
                      <v-toolbar flat>
                        <v-toolbar-title>Parents Of Role</v-toolbar-title>
                        <v-divider class="mx-4" inset vertical></v-divider>
                        <v-spacer></v-spacer>
                        <v-btn
                          color="primary"
                          dark
                          fab
                          small
                          @click="addParent"
                          v-show="hasAdminAccess"
                        >
                          <v-icon>mdi-plus</v-icon>
                        </v-btn>
                      </v-toolbar>
                    </template>

                    <template v-slot:item.name="props">
                      <v-edit-dialog :return-value="props.item.name">
                        {{ props.item.name }}
                        <template v-slot:input>
                          <v-combobox
                            v-model="props.item.name"
                            label="Edit Parent"
                            :items="states"
                            :disabled="!hasAdminAccess"
                            single-line
                          >
                          </v-combobox>
                        </template>
                      </v-edit-dialog>
                    </template>

                    <template v-slot:item.actions="{ item }">
                      <v-icon @click="deleteParent(item)" :disabled="!hasAdminAccess">
                        mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                </v-tab-item>

                <v-tab-item>
                  <v-data-table
                    :headers="headers"
                    :items="childs"
                    class="elevation-0"
                    height="330"
                    hide-default-footer
                    disable-pagination
                    fixed-header
                  >
                    <template v-slot:top>
                      <v-toolbar flat>
                        <v-toolbar-title>Childs Of Role</v-toolbar-title>
                        <v-divider class="mx-4" inset vertical></v-divider>
                        <v-spacer></v-spacer>
                        <v-btn
                          color="primary"
                          dark
                          fab
                          small
                          @click="addChild"
                          v-show="hasEditAccess"
                        >
                          <v-icon>mdi-plus</v-icon>
                        </v-btn>
                      </v-toolbar>
                    </template>

                    <template v-slot:item.name="props">
                      <v-edit-dialog :return-value="props.item.name">
                        {{ props.item.name }}
                        <template v-slot:input>
                          <v-combobox
                            v-model="props.item.name"
                            label="Edit Child"
                            :items="states"
                            :disabled="!hasEditAccess"
                            single-line
                          >
                          </v-combobox>
                        </template>
                      </v-edit-dialog>
                    </template>

                    <template v-slot:item.actions="{ item }">
                      <v-icon @click="deleteChild(item)" :disabled="!hasEditAccess">
                        mdi-delete
                      </v-icon>
                    </template>
                  </v-data-table>
                </v-tab-item>
              </v-tabs>
            </v-card>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="close" :disabled="loading">
              Cancel
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              type="submit"
              :disabled="invalid"
              :loading="loading"
              v-show="hasEditAccess"
            >
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit, Watch, VModel, Ref } from "vue-property-decorator";
import { mainStore, roleStore } from "@/store";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { IVueBelongsMembers } from "@/interfaces/vue-models";
import { IRoleRelationship } from "@/interfaces/greenplum";
import _ from "lodash";

// register validation rules
extend("required_with_space", {
  computesRequired: true,
  message: "{_field_} must contain at least one character",
  validate(value) {
    return {
      required: true,
      valid: ["", null, undefined].indexOf(value) === -1,
    };
  },
});

@Component({
  components: {
    ValidationObserver,
    ValidationProvider,
  },
})
export default class MembersEditDialog extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  @Prop()
  editedItem!: IVueBelongsMembers;

  @Emit()
  needRefresh(_payload: any) {}

  @VModel({ type: Boolean })
  dialog!: boolean;

  loading: boolean = false;
  rolname: string = "";
  childs: any[] = [];
  parents: any[] = [];

  async emitPromise(method: any, ...params: any[]) {
    let listener = this.$listeners[method] || this.$attrs[method] || this[method];
    if (listener && !Array.isArray(listener)) {
      //one can additionally wrap this in try/catch if needed and handle the error further
      let res = await listener(...params);
      return res === undefined || res;
    }
    return false;
  }

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  get hasEditAccess(): boolean {
    if (mainStore.hasAdminAccess) {
      return true;
    }

    return !!_.find(mainStore.currentAccess, {
      type_of_entity: "Role",
      role: this.rolname,
    });
  }

  deleteParent(item: any) {
    const editedIndex = this.parents.indexOf(item);
    this.parents.splice(editedIndex, 1);
  }

  addParent() {
    const empty = { name: "" };
    this.parents.unshift(empty);
  }

  deleteChild(item: any) {
    const editedIndex = this.childs.indexOf(item);
    this.childs.splice(editedIndex, 1);
  }

  addChild() {
    const empty = { name: "" };
    this.childs.unshift(empty);
  }

  headers = [
    {
      text: "Role Name",
      align: "start",
      value: "name",
      sortable: false,
    },
    { text: "Actions", value: "actions", sortable: false },
  ];

  get states() {
    return _.map(roleStore.roles, "rolname");
  }

  foundAppended(olds: string[], news: any[]): string[] {
    return _.chain(news)
      .map("name")
      .difference(olds)
      .value();
  }

  foundRemoved(olds: string[], news: any[]): string[] {
    return _.chain(olds)
      .difference(_.map(news, "name"))
      .value();
  }

  relationsForRemove(): IRoleRelationship[] {
    const remParent = this.foundRemoved(this.editedItem.parents, this.parents);
    const remChild = this.foundRemoved(this.editedItem.childs, this.childs);

    return _.union(
      _.map(remParent, (item) => {
        return {
          rolname: item,
          member: this.rolname,
        };
      }),
      _.map(remChild, (item) => {
        return {
          rolname: this.rolname,
          member: item,
        };
      }),
    );
  }

  relationsForAppend(): IRoleRelationship[] {
    const addParent = this.foundAppended(this.editedItem.parents, this.parents);
    const addChild = this.foundAppended(this.editedItem.childs, this.childs);

    return _.union(
      _.map(addParent, (item) => {
        return {
          rolname: item,
          member: this.rolname,
        };
      }),
      _.map(addChild, (item) => {
        return {
          rolname: this.rolname,
          member: item,
        };
      }),
    );
  }

  async save() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loading = true;
    try {
      await this.emitPromise("need-refresh", {
        remove: this.relationsForRemove(),
        append: this.relationsForAppend(),
      });
    } finally {
      this.loading = false;
      this.close();
    }
  }

  @Watch("dialog")
  async open(val: boolean) {
    if (val === true) {
      this.editItem(this.editedItem);
      await roleStore.getRoles();
    }
  }

  editItem(item: IVueBelongsMembers) {
    this.rolname = item.rolname;
    this.parents = _.map(item.parents, (parent) => {
      return {
        name: parent,
      };
    });
    this.childs = _.map(item.childs, (child) => {
      return {
        name: child,
      };
    });
  }

  close() {
    this.dialog = false;
  }
}
</script>
