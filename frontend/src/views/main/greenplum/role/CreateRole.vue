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
            <div class="text-h5">Create Role</div>
          </v-card-title>

          <v-card-text>
            <validation-provider
              v-slot="{ errors }"
              name="Role Name"
              rules="required_with_space"
            >
              <v-text-field
                v-model="roleName"
                label="Role Name"
                :error-messages="errors"
              ></v-text-field>
            </validation-provider>

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

            <v-btn @click="generateKey" class="mb-6 mt-2"> GENERATE PASSWORD </v-btn>

            <v-row no-gutters>
              <v-col cols="12" md="6">
                <div class="subheading secondary--text text--lighten-2">
                  User is superuser
                  <span v-if="isSuperuser">(currently is a superuser)</span>
                  <span v-else>(currently is not a superuser)</span>
                </div>
                <v-checkbox v-model="isSuperuser" label="Is Superuser"></v-checkbox>

                <div class="subheading secondary--text text--lighten-2">
                  User is create role
                  <span v-if="isCreateRole">(currently is a create role)</span>
                  <span v-else>(currently is not a create role)</span>
                </div>
                <v-checkbox v-model="isCreateRole" label="Is Create Role"></v-checkbox>

                <div class="subheading secondary--text text--lighten-2">
                  User is create database
                  <span v-if="isCreateDB">(currently is a create database)</span>
                  <span v-else>(currently is not a create database)</span>
                </div>
                <v-checkbox
                  v-model="isCreateDB"
                  label="Is Create Database"
                ></v-checkbox>
              </v-col>
              <v-col>
                <div class="subheading secondary--text text--lighten-2">
                  User is inherit <span v-if="isInherit">(currently is a inherit)</span>
                  <span v-else>(currently is not a inherit)</span>
                </div>
                <v-checkbox v-model="isInherit" label="Is Inherit"></v-checkbox>

                <div class="subheading secondary--text text--lighten-2">
                  User is login <span v-if="isLogin">(currently is a login)</span>
                  <span v-else>(currently is not a login)</span>
                </div>
                <v-checkbox v-model="isLogin" label="Is Login"></v-checkbox>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel" :disabled="loading">Cancel</v-btn>
            <v-btn type="reset" :disabled="loading">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid" :loading="loading">Save</v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Ref } from "vue-property-decorator";
import { IRoleProfileCreate } from "@/interfaces/greenplum";
import { roleStore } from "@/store";
import { required } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import { generateString } from "@/utils/generate-string";

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
export default class CreateRole extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  valid: boolean = false;
  roleName: string = "";
  password: string = "";
  showPassword: boolean = true;
  isSuperuser: boolean = false;
  isCreateRole: boolean = false;
  isCreateDB: boolean = false;
  isInherit: boolean = true;
  isLogin: boolean = true;

  activated() {
    this.onReset();
  }

  onReset() {
    this.roleName = "";
    this.password = generateString();
    this.isSuperuser = false;
    this.isCreateRole = false;
    this.isCreateDB = false;
    this.isInherit = true;
    this.isLogin = true;
    this.observer.reset();
  }

  cancel() {
    this.$router.back();
  }

  generateKey() {
    this.password = generateString();
  }

  async onSubmit() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loading = true;
    try {
      const updatedProfile: IRoleProfileCreate = {
        rolname: this.roleName,
        password: this.password,
        rolsuper: this.isSuperuser,
        rolcreaterole: this.isCreateRole,
        rolcreatedb: this.isCreateDB,
        rolinherit: this.isInherit,
        rolcanlogin: this.isLogin,
      };

      await roleStore.createRole(updatedProfile);
    } finally {
      this.loading = false;
      this.$router.push({
        name: "main-greenplum-roles",
      });
    }
  }
}
</script>
