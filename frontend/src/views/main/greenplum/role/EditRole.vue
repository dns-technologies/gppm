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
            <div class="text-h5">Edit Role</div>
          </v-card-title>

          <v-card-text>
            <div class="my-3">
              <div class="subheading secondary--text text--lighten-2">Role</div>
              <div v-if="role" class="title primary--text text--darken-2">
                {{ role.rolname | rereplaceSpaces }}
              </div>
              <div v-else class="title primary--text text--darken-2">-----</div>
            </div>

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
                  User is inherit
                  <span v-if="isInherit">(currently is a inherit)</span>
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
            <v-row no-gutters>
              <v-col>
                <v-checkbox
                  v-model="setPassword"
                  label="Override Password"
                ></v-checkbox>
              </v-col>

              <v-col>
                <!-- password -->
                <validation-provider
                  v-slot="{ errors }"
                  :debounce="100"
                  name="Password"
                  vid="password1"
                  :rules="{ required: setPassword }"
                >
                  <v-text-field
                    v-model="password1"
                    :disabled="!setPassword"
                    label="Password"
                    :error-messages="errors"
                    :append-icon="showPassword1 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="showPassword1 ? 'text' : 'password'"
                    @click:append="showPassword1 = !showPassword1"
                  ></v-text-field>
                </validation-provider>

                <!-- password confirmation -->
                <validation-provider
                  v-slot="{ errors }"
                  :debounce="100"
                  name="Password confirmation"
                  vid="password2"
                  :rules="{
                    required: setPassword,
                    confirmed: setPassword ? 'password1' : false,
                  }"
                >
                  <v-text-field
                    v-model="password2"
                    :disabled="!setPassword"
                    label="Confirm Password"
                    :error-messages="errors"
                    :append-icon="showPassword2 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="showPassword2 ? 'text' : 'password'"
                    @click:append="showPassword2 = !showPassword2"
                  ></v-text-field>
                </validation-provider>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel" :disabled="loading">Cancel</v-btn>
            <v-btn type="reset" :disabled="loading">Reset</v-btn>
            <v-btn
              type="submit"
              :disabled="invalid"
              v-show="hasAdminAccess"
              :loading="loading"
              >Save</v-btn
            >
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Ref } from "vue-property-decorator";
import { IRoleProfile, IRoleProfileUpdate } from "@/interfaces/greenplum";
import { mainStore, roleStore } from "@/store";
import { required, confirmed } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import _ from "lodash";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
extend("confirmed", { ...confirmed, message: "Passwords do not match" });
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
  filters: {
    rereplaceSpaces(name: string): string {
      if (name?.trim() === "") {
        return name.replace(/\s/g, "•");
      }
      return name;
    },
  },
})
export default class EditRole extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  valid: boolean = true;
  roleName: string = "";
  showPassword1: boolean = false;
  showPassword2: boolean = false;
  isSuperuser: boolean = false;
  isCreateRole: boolean = false;
  isCreateDB: boolean = false;
  isInherit: boolean = true;
  isLogin: boolean = true;
  setPassword: boolean = false;
  password1: string = "";
  password2: string = "";
  role: IRoleProfile | null = null;

  get hasAdminAccess(): boolean {
    return mainStore.hasAdminAccess;
  }

  async refresh() {
    const before = (this.role = this.currentRole());
    this.onReset();
    await roleStore.getRoles();
    this.role = this.currentRole();
    if (!_.isEqual(before, this.role)) {
      this.onReset();
    }
  }

  async activated() {
    await this.refresh();
  }

  onReset() {
    this.setPassword = false;
    this.password1 = "";
    this.password2 = "";
    if (this.role) {
      this.roleName = this.role.rolname;
      this.isSuperuser = this.role.rolsuper;
      this.isCreateRole = this.role.rolcreaterole;
      this.isCreateDB = this.role.rolcreatedb;
      this.isInherit = this.role.rolinherit;
      this.isLogin = this.role.rolcanlogin;
    } else {
      this.roleName = "";
      this.isSuperuser = false;
      this.isCreateRole = false;
      this.isCreateDB = false;
      this.isInherit = true;
      this.isLogin = true;
    }
    this.observer.reset();
  }

  cancel() {
    this.$router.back();
  }

  async onSubmit() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    if (!this.role) {
      return;
    }

    this.loading = true;
    try {
      const updatedProfile: IRoleProfileUpdate = {
        rolname: this.roleName,
        rolsuper: this.isSuperuser,
        rolcreaterole: this.isCreateRole,
        rolcreatedb: this.isCreateDB,
        rolinherit: this.isInherit,
        rolcanlogin: this.isLogin,
        password: this.setPassword ? this.password1 : undefined,
      };

      await roleStore.updateRole({
        rolname: this.role.rolname,
        role: updatedProfile,
      });
    } finally {
      this.loading = false;
      this.$router.push({
        name: "main-greenplum-roles",
      });
    }
  }

  currentRole(): IRoleProfile | null {
    const { oid } = this.$router.currentRoute.params;
    return roleStore.adminOneRole(+oid);
  }
}
</script>
