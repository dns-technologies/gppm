<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="save" :class="{ 'no-click': loading }">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <validation-provider name="Resource Group" rules="required_with_space">
              <v-text-field
                v-model="resourceGroup"
                label="Resource Group"
                hide-details
                outlined
                :disabled="readonly"
                class="pb-4"
              >
              </v-text-field>
            </validation-provider>

            <v-card>
              <v-tabs vertical>
                <v-tab>
                  <v-icon left>mdi-settings</v-icon>
                  Settings
                </v-tab>

                <v-tab>
                  <v-icon left>mdi-account-box</v-icon>
                  Members
                </v-tab>

                <v-tab-item>
                  <v-row class="pb-8 pt-4 px-6">
                    <v-col cols="12" class="py-0">
                      <v-subheader class="pl-2"> Concurrency </v-subheader>
                      <v-slider
                        v-model="concurrency"
                        thumb-label="always"
                        hide-details
                        :max="slider.concurrency_max"
                        :min="slider.concurrency_min"
                      ></v-slider>
                    </v-col>

                    <v-col cols="12" class="py-0">
                      <validation-provider name="CPU" rules="min_value:1">
                        <v-subheader class="pl-2"> CPU (%) </v-subheader>
                        <v-slider
                          v-model="cpu"
                          thumb-label="always"
                          hide-details
                          :max="slider.cpu_rate_limit_max"
                          :min="slider.cpu_rate_limit_min"
                        ></v-slider>
                      </validation-provider>
                    </v-col>

                    <v-col cols="12" class="py-0">
                      <v-subheader class="pl-2"> Memory (%) </v-subheader>
                      <v-slider
                        v-model="memory"
                        thumb-label="always"
                        hide-details
                        :max="slider.memory_limit_max"
                        :min="slider.memory_limit_min"
                      ></v-slider>
                    </v-col>
                  </v-row>
                </v-tab-item>

                <v-tab-item>
                  <v-data-table
                    :headers="headers"
                    :items="members"
                    class="elevation-0"
                    height="330"
                    hide-default-footer
                    disable-pagination
                    fixed-header
                  >
                    <template v-slot:top>
                      <v-toolbar flat>
                        <v-toolbar-title>Members</v-toolbar-title>
                        <v-divider class="mx-4" inset vertical></v-divider>
                        <v-spacer></v-spacer>
                        <v-btn
                          color="primary"
                          dark
                          @click="addMember"
                          v-show="hasAdminAccess"
                        >
                          New Member
                        </v-btn>
                      </v-toolbar>
                    </template>

                    <template v-slot:item.name="props">
                      <v-edit-dialog :return-value="props.item.name">
                        {{ props.item.name }}
                        <template v-slot:input>
                          <v-combobox
                            v-model="props.item.name"
                            label="Edit Member"
                            :items="states"
                            :disabled="!hasAdminAccess"
                            single-line
                          >
                          </v-combobox>
                        </template>
                      </v-edit-dialog>
                    </template>

                    <template v-slot:item.actions="{ item }">
                      <v-icon @click="deleteMember(item)" :disabled="!hasAdminAccess">
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
              v-show="hasAdminAccess"
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
import { mainStore, resourceStore, roleStore } from "@/store";
import { min_value } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { IResourceGroup } from "@/interfaces/greenplum";
import _ from "lodash";

// register validation rules
extend("min_value", { ...min_value, message: "CPU (%) must be above zero" });
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
export default class ResourceEditDialog extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  @Prop()
  editedItem!: IResourceGroup;

  @Emit()
  needRefresh(_payload: any) {}

  @VModel({ type: Boolean })
  dialog!: boolean;

  formTitle: string = "";
  readonly: boolean = true;
  loading: boolean = false;

  resourceGroup: string = "";
  concurrency: number = 0;
  cpu: number = 0;
  memory: number = 0;
  members: any[] = [];

  cpu_rate_limit_def: number = 0;
  memory_limit_def: number = 0;

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

  deleteMember(item: any) {
    const editedIndex = this.members.indexOf(item);
    this.members.splice(editedIndex, 1);
  }

  addMember() {
    const emptyMember = { name: "" };
    this.members.unshift(emptyMember);
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
    return this.resourceGroup === "admin_group"
      ? _.chain(roleStore.roles).filter("rolsuper").map("rolname").value()
      : _.map(roleStore.roles, "rolname");
  }

  async save() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loading = true;
    try {
      let payload: IResourceGroup = {
        oid: -1, // Игнорируем
        name: this.resourceGroup,
        concurrency: this.concurrency,
        memory_limit: this.memory,
        cpu_rate_limit: this.cpu,
        group_members: _.map(this.members, "name"),
      };

      await this.emitPromise("need-refresh", {
        method: this.readonly ? "UPDATE" : "CREATE",
        data: payload,
      });
    } finally {
      this.loading = false;
      this.close();
    }
  }

  @Watch("dialog")
  async open(val: boolean) {
    if (val === true) {
      if (this.editedItem) {
        this.editItem(this.editedItem);
      } else {
        this.createItem();
      }
      await roleStore.getRoles();
    }
  }

  createItem() {
    this.formTitle = "New Resource Group";
    this.readonly = false;
    this.resourceGroup = "";
    this.concurrency = 0;
    this.cpu = 0;
    this.memory = 0;
    this.members = [];
    this.cpu_rate_limit_def = 0;
    this.memory_limit_def = 0;
  }

  get slider() {
    const limits = resourceStore.resourceGroupsLimits;

    return {
      concurrency_min: limits.concurrency_min,
      cpu_rate_limit_min: limits.cpu_rate_limit_min,
      memory_limit_min: limits.memory_limit_min,
      concurrency_max: limits.concurrency_max,
      cpu_rate_limit_max: limits.cpu_rate_limit_max + this.cpu_rate_limit_def,
      memory_limit_max: limits.memory_limit_max + this.memory_limit_def,
    };
  }

  editItem(item: IResourceGroup) {
    this.formTitle = "Edit Resource Group";
    this.readonly = true;
    this.resourceGroup = item.name;
    this.concurrency = item.concurrency;
    this.memory = item.memory_limit;
    this.cpu = item.cpu_rate_limit;
    this.members = _.map(item.group_members, (member) => {
      return {
        name: member,
      };
    });
    this.cpu_rate_limit_def = item.cpu_rate_limit;
    this.memory_limit_def = item.memory_limit;
  }

  close() {
    this.dialog = false;
  }

  created() {
    this.createItem();
  }
}
</script>
