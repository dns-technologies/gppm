<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="save" :class="{ 'no-click': loading }">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <validation-provider name="Role" rules="required_with_space">
              <v-combobox
                v-model="grantee"
                label="Role"
                :items="states"
                hide-details
                outlined
                :disabled="readonly"
                class="pb-4"
              >
              </v-combobox>
            </validation-provider>

            <v-list subheader two-line>
              <v-subheader>Permisson Rules</v-subheader>

              <template v-for="item in items">
                <v-list-item :key="item.title">
                  <v-list-item-action>
                    <v-checkbox v-model="item.value"></v-checkbox>
                  </v-list-item-action>

                  <v-list-item-content
                    @click="item.value = !item.value"
                    class="v-list-item--link"
                  >
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>

            <v-list subheader two-line v-if="optional && optional.length">
              <v-subheader>Optional Params </v-subheader>

              <template v-for="item in optional">
                <v-list-item
                  :key="item.title"
                  @click="emitOptionalEvents(item.name)"
                  :disabled="!grantee"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
          </v-card-text>

          <v-card-actions>
            <v-checkbox
              dense
              v-model="grantOption"
              class="my-0 py-0 ml-1"
              hide-details
              label="Grant Option"
            ></v-checkbox>
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
import { roleStore } from "@/store";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
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
export default class AclPermissionDialog extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  @Prop()
  editedItem!: any;

  @Prop()
  template!: any[];

  @Prop()
  optionalTemplate!: any[];

  @Emit()
  optionalEvents(_payload: any) {}

  @Emit()
  needRefresh(_payload: any) {}

  @VModel({ type: Boolean })
  dialog!: boolean;

  formTitle: string = "";
  readonly: boolean = true;
  loading: boolean = false;

  items: any[] = [];
  optional: any[] = [];
  grantee: string = "";
  defaultGrantee: string = "";
  grantOption: boolean = false;

  get states() {
    return _.map(roleStore.roles, "rolname");
  }

  async emitPromise(method: any, ...params: any[]) {
    let listener = this.$listeners[method] || this.$attrs[method] || this[method];
    if (listener && !Array.isArray(listener)) {
      //one can additionally wrap this in try/catch if needed and handle the error further
      let res = await listener(...params);
      return res === undefined || res;
    }
    return false;
  }

  async save() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loading = true;
    try {
      let payload = {
        grantee: this.grantee,
        grantOption: this.grantOption,
      };
      for (const key in this.items) {
        let element = this.items[key];
        payload[element["name"]] = element["value"];
      }
      await this.emitPromise("need-refresh", payload);
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

  emitOptionalEvents(optionName: string) {
    if (this.grantee) {
      let payload = {
        grantee: this.grantee,
        grantOption: this.grantOption,
        optionName: optionName,
      };

      this.optionalEvents(payload);
    }
  }

  editItem(item: any) {
    this.formTitle = "Edit Rule";
    this.readonly = true;
    this.grantOption = false;
    this.grantee = item.grantee;

    let items = _.cloneDeep(this.template);

    for (let key in items) {
      let element = items[key];
      element["value"] = item[element["name"]];
    }

    this.items = items;
    this.optional = this.optionalTemplate;
  }

  createItem() {
    this.formTitle = "New Rule";
    this.readonly = false;
    this.grantOption = false;
    this.grantee = this.defaultGrantee;
    this.items = _.cloneDeep(this.template);
    this.optional = this.optionalTemplate;
  }

  close() {
    this.dialog = false;
  }

  created() {
    this.createItem();
  }
}
</script>
