<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="save" :class="{ 'no-click': loading }">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <validation-provider name="User" rules="required">
              <v-autocomplete
                :items="allUsers"
                v-model="selectedUser"
                class="mb-4"
                flat
                hide-details
                item-text="email"
                item-value="email"
                return-object
                label="User"
                outlined
              >
                <template v-slot:selection="{ item }">
                  {{ item.email }}
                </template>
                <template v-slot:item="{ item }">
                  <v-list-item-avatar
                    color="indigo"
                    class="text-h5 font-weight-light white--text"
                  >
                    {{ item.email.charAt(0) }}
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title v-text="item.email"></v-list-item-title>
                    <v-list-item-subtitle>{{ item.full_name }}</v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </v-autocomplete>
            </validation-provider>

            <v-card :loading="loadingCard > 0">
              <v-tabs v-model="tab">
                <v-tab> Role </v-tab>
                <v-tab> Database </v-tab>
                <v-tab> Schema </v-tab>

                <v-tab-item>
                  <v-container fluid>
                    <validation-provider
                      name="Role First"
                      :rules="{ required_with_space: tab === 0 }"
                    >
                      <v-combobox
                        :items="allRoles"
                        v-model="selectedRole"
                        flat
                        hide-details
                        label="Role"
                        outlined
                      >
                      </v-combobox>
                    </validation-provider>
                  </v-container>
                </v-tab-item>

                <v-tab-item>
                  <v-container fluid>
                    <validation-provider
                      name="Database Second"
                      :rules="{ required_with_space: tab === 1 }"
                    >
                      <v-combobox
                        :items="allDatabases"
                        :value="selectedDatabase"
                        @change="changedDatabase"
                        flat
                        hide-details
                        label="Database"
                        outlined
                      >
                      </v-combobox>
                    </validation-provider>
                  </v-container>
                </v-tab-item>

                <v-tab-item>
                  <v-container fluid>
                    <validation-provider
                      name="Database Third"
                      :rules="{ required_with_space: tab === 2 }"
                    >
                      <v-combobox
                        :items="allDatabases"
                        :value="selectedDatabase"
                        @change="changedDatabase"
                        flat
                        hide-details
                        label="Database"
                        class="mb-4"
                        outlined
                      >
                      </v-combobox>
                    </validation-provider>

                    <validation-provider
                      name="Schema Third"
                      :rules="{ required_with_space: tab === 2 }"
                    >
                      <v-combobox
                        :items="allSchemas"
                        v-model="selectedSchema"
                        flat
                        hide-details
                        label="Schema"
                        outlined
                      >
                      </v-combobox>
                    </validation-provider>
                  </v-container>
                </v-tab-item>
              </v-tabs>
            </v-card>

            <v-checkbox v-model="is_active" label="Is Active" class="pb-0"></v-checkbox>

            <v-alert
              color="cyan"
              border="left"
              elevation="2"
              colored-border
              type="warning"
              class="mb-0"
              dense
              prominent
            >
              The rule is applied only to the <strong>selected context.</strong> <br />
              If you press save, rule for
              <strong>{{ nameOfTabByIndex(tab) }}</strong>
              will be apply!
            </v-alert>
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
import { aclStore, adminStore, mainStore, roleStore } from "@/store";
import { required } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { IAclDatabase, IAclSchema } from "@/interfaces/greenplum";
import { IAccess, IUserProfile } from "@/interfaces/admin";
import _ from "lodash";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
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
export default class AccessEditDialog extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  @Prop()
  editedItem!: IAccess;

  @Emit()
  needRefresh(_payload: any) {}

  @VModel({ type: Boolean })
  dialog!: boolean;

  selectedUser: IUserProfile | null = null;
  selectedRole: string | null = null;
  selectedDatabase: string | null = null;
  databases: IAclDatabase[] = [];
  selectedSchema: string | null = null;
  schemas: IAclSchema[] = [];
  is_active: boolean = true;

  formTitle: string = "";
  readonly: boolean = true;
  loading: boolean = false;
  loadingCard: number = 0;
  tab: number = 0;

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

    const userId = this.selectedUser?.id;
    const contextId = mainStore.currentContext?.id;
    if (!userId || !contextId) {
      return;
    }

    const id = this.editedItem ? this.editedItem.id : -1;
    const type_of_entity = this.nameOfTabByIndex(this.tab);

    let role: string | null = null;
    let database: string | null = null;
    let schema: string | null = null;

    switch (type_of_entity) {
      case "Database":
        database = this.selectedDatabase;
        break;
      case "Schema":
        database = this.selectedDatabase;
        schema = this.selectedSchema;
        break;
      default:
        role = this.selectedRole;
        break;
    }

    this.loading = true;
    try {
      let payload: IAccess = {
        id: id,
        context_id: contextId,
        user_id: userId,
        role: role,
        database: database,
        db_schema: schema,
        type_of_entity: type_of_entity,
        is_active: this.is_active,
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
    if (val !== true) {
      return;
    }

    ++this.loadingCard;
    try {
      if (this.editedItem) {
        this.editItem(this.editedItem);
      } else {
        this.createItem();
      }
      const data = await Promise.all([
        aclStore.getDatabases(),
        adminStore.getUsers(),
        roleStore.getRoles(),
      ]);
      this.databases = data[0];
    } finally {
      --this.loadingCard;
    }
  }

  get allUsers(): IUserProfile[] {
    return adminStore.users;
  }

  get allRoles(): string[] {
    return _.map(roleStore.roles, "rolname");
  }

  get allDatabases(): string[] {
    return _.map(this.databases, "name");
  }

  get allSchemas(): string[] {
    return _.map(this.schemas, "name");
  }

  nameOfTabByIndex(index: number): string {
    const data = {
      0: "Role",
      1: "Database",
      2: "Schema",
    };

    return data[index];
  }

  async changedDatabase(database: any) {
    ++this.loadingCard;
    try {
      this.selectedDatabase = database;
      this.schemas = await aclStore.getSchemas(database);
    } finally {
      --this.loadingCard;
    }
  }

  async createItem() {
    this.formTitle = "New Access Rule";
    this.readonly = false;
    this.selectedUser = null;
    this.is_active = true;
    this.selectedRole = null;
    this.selectedDatabase = null;
    this.selectedSchema = null;
  }

  async editItem(item: IAccess) {
    this.formTitle = "Edit Access Rule";
    this.readonly = true;
    this.is_active = item.is_active;
    this.selectedUser = _.find(adminStore.users, { id: item.user_id }) || null;

    this.selectedRole = item.role;
    this.selectedDatabase = item.database;
    this.selectedSchema = item.db_schema;

    switch (item.type_of_entity) {
      case "Database":
        this.tab = 1;
        break;
      case "Schema":
        this.tab = 2;
        break;
      default:
        this.tab = 0;
        break;
    }

    await this.changedDatabase(this.selectedDatabase);
  }

  close() {
    this.dialog = false;
  }

  created() {
    this.createItem();
  }
}
</script>
