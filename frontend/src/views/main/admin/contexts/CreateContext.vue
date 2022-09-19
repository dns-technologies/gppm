<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form
        @submit.prevent="onSubmit"
        @reset.prevent="onReset"
        :class="{ 'no-click': loading }"
      >
        <v-card class="ma-3 elevation-10">
          <v-card-title primary-title class="white--text indigo">
            <div class="text-h5">Create Context</div>
          </v-card-title>

          <v-card-text>
            <template>
              <v-row class="grid-of-elements">
                <!-- alias -->
                <v-col cols="12">
                  <validation-provider
                    v-slot="{ errors }"
                    name="Alias"
                    rules="required"
                  >
                    <v-text-field
                      v-model="alias"
                      label="Alias"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- server -->
                <v-col cols="12" md="6">
                  <validation-provider
                    v-slot="{ errors }"
                    name="Server"
                    rules="required"
                  >
                    <v-text-field
                      v-model="server"
                      label="Server"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- port -->
                <v-col cols="12" md="6">
                  <validation-provider v-slot="{ errors }" name="Port" rules="required|numeric">
                    <v-text-field
                      v-model="port"
                      label="Port"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- database -->
                <v-col cols="12">
                  <validation-provider
                    v-slot="{ errors }"
                    name="Database"
                    rules="required"
                  >
                    <v-text-field
                      v-model="database"
                      label="Database"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- role -->
                <v-col cols="12" md="6">
                  <validation-provider v-slot="{ errors }" name="Role" rules="required">
                    <v-text-field
                      v-model="role"
                      label="Role"
                      :error-messages="errors"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- pass -->
                <v-col cols="12" md="6">
                  <validation-provider
                    v-slot="{ errors }"
                    name="Password"
                    vid="password"
                    rules="required"
                  >
                    <v-text-field
                      v-model="password"
                      label="Password"
                      :error-messages="errors"
                      :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="showPassword ? 'text' : 'password'"
                      @click:append="showPassword = !showPassword"
                    ></v-text-field>
                  </validation-provider>
                </v-col>

                <!-- is active -->
                <v-col cols="12">
                  <div class="subheading secondary--text text--lighten-2">
                    Context is active <span v-if="isActive">(currently active)</span>
                    <span v-else>(currently not active)</span>
                  </div>
                  <v-checkbox v-model="isActive" label="Is Active"></v-checkbox>
                </v-col>
              </v-row>
            </template>
            <template>
              <v-dialog v-model="dialog" max-width="350">
                <v-card :color="validateStatus ? 'success' : 'error'">
                  <div v-if="validateStatus">
                    <v-card-title class="text-h6 justify-center">
                      Connection Success
                    </v-card-title>

                    <v-card-text>
                      The connection test completed successfully. You can add this
                      connection as a contex.
                    </v-card-text>
                  </div>
                  <div v-else>
                    <v-card-title class="text-h6 justify-center">
                      Connection Fail
                    </v-card-title>

                    <v-card-text>
                      A connection could not be established with the specified
                      connection options.
                    </v-card-text>
                  </div>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn text @click="dialog = false"> Close </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </template>
          </v-card-text>
          <v-card-actions>
            <v-btn
              @click="checkConnection"
              :disabled="invalid || loading"
              :loading="loadingCheck"
              >Check Connection</v-btn
            >
            <v-spacer></v-spacer>
            <v-btn @click="cancel" :disabled="loading">Cancel</v-btn>
            <v-btn type="reset" :disabled="loading">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid || loading" :loading="loadingSave"
              >Save</v-btn
            >
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Ref, Watch } from "vue-property-decorator";
import { IContextCreate, IContextMini } from "@/interfaces/admin";
import { adminStore } from "@/store";
import { required, numeric } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
extend("numeric", { ...numeric, message: "{_field_} must be a number" });

@Component({
  components: {
    ValidationObserver,
    ValidationProvider,
  },
})
export default class CreateContext extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  dialog: boolean = false;
  validateStatus: boolean = false;
  loadingSave: boolean = false;
  loadingCheck: boolean = false;
  showPassword: boolean = false;
  loading: boolean = false;
  valid: boolean = false;
  alias: string = "";
  server: string = "";
  role: string = "";
  isActive: boolean = true;
  port: number = 5432;
  password: string = "";
  database: string = "template1";

  activated() {
    this.onReset();
  }

  @Watch("loadingCheck")
  @Watch("loadingSave")
  changeLoading(value: boolean) {
    this.loading = value;
  }

  onReset() {
    this.alias = "";
    this.server = "";
    this.port = 5432;
    this.role = "";
    this.password = "";
    this.database = "template1";
    this.isActive = true;
    this.observer.reset();
  }

  cancel() {
    this.$router.back();
  }

  async checkConnection() {
    const validateContext: IContextMini = {
      server: this.server,
      role: this.role,
      port: this.port,
      database: this.database,
      password: this.password,
    };

    this.loadingCheck = true;
    this.validateStatus = false;
    try {
      this.validateStatus = await adminStore.validateContext(validateContext);
    } finally {
      this.loadingCheck = false;
      this.dialog = true;
    }
  }

  async onSubmit() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loadingSave = true;
    try {
      const updatedContext: IContextCreate = {
        alias: this.alias,
        server: this.server,
        port: this.port,
        role: this.role,
        password: this.password,
        database: this.database,
        is_active: this.isActive,
      };

      await adminStore.createContext(updatedContext);
    } finally {
      this.loadingSave = false;
      this.$router.push({
        name: "main-admin-contexts",
      });
    }
  }
}
</script>

<style scoped>
.grid-of-elements {
  padding: 12px 0px 0px 0px;
}
.grid-of-elements > div {
  padding: 0px 12px;
}
</style>