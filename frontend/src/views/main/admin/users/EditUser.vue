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
            <div class="text-h5">Edit User</div>
          </v-card-title>

          <v-card-text>
            <template>
              <div class="my-3">
                <div class="subheading secondary--text text--lighten-2">User</div>
                <div v-if="user" class="title primary--text text--darken-2">
                  {{ user.email }}
                </div>
                <div v-else class="title primary--text text--darken-2">-----</div>
              </div>
              <!-- full name -->
              <v-text-field v-model="fullName" label="Full Name"></v-text-field>

              <!-- email -->
              <validation-provider
                v-slot="{ errors }"
                rules="required|email"
                name="Email"
              >
                <v-text-field
                  v-model="email"
                  label="Email"
                  :error-messages="errors"
                ></v-text-field>
              </validation-provider>

              <!-- is superuser -->
              <div class="subheading secondary--text text--lighten-2">
                User is superuser
                <span v-if="isSuperuser">(currently is a superuser)</span>
                <span v-else>(currently is not a superuser)</span>
              </div>
              <v-checkbox v-model="isSuperuser" label="Is Superuser"></v-checkbox>

              <!-- is active -->
              <div class="subheading secondary--text text--lighten-2">
                User is active <span v-if="isActive">(currently active)</span>
                <span v-else>(currently not active)</span>
              </div>
              <v-checkbox v-model="isActive" label="Is Active"></v-checkbox>
              <v-row>
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
            </template>
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
import { IUserProfile, IUserProfileUpdate } from "@/interfaces/admin";
import { adminStore } from "@/store";
import { required, confirmed, email } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";
import _ from "lodash";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
extend("confirmed", { ...confirmed, message: "Passwords do not match" });
extend("email", { ...email, message: "Invalid email address" });

@Component({
  components: {
    ValidationObserver,
    ValidationProvider,
  },
})
export default class EditUser extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  valid: boolean = true;
  fullName: string = "";
  email: string = "";
  isActive: boolean = true;
  isSuperuser: boolean = false;
  setPassword: boolean = false;
  password1: string = "";
  password2: string = "";
  showPassword1: boolean = false;
  showPassword2: boolean = false;
  user: IUserProfile | null = null;

  async refresh() {
    const before = (this.user = this.currentUser());
    this.onReset();
    await adminStore.getUsers();
    this.user = this.currentUser();
    if (!_.isEqual(before, this.user)) {
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
    if (this.user) {
      this.fullName = this.user.full_name;
      this.email = this.user.email;
      this.isActive = this.user.is_active;
      this.isSuperuser = this.user.is_superuser;
    } else {
      this.fullName = "";
      this.email = "";
      this.isActive = true;
      this.isSuperuser = false;
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

    if (!this.user) {
      return;
    }

    this.loading = true;
    try {
      const updatedProfile: IUserProfileUpdate = {
        email: this.email,
        full_name: this.fullName,
        is_active: this.isActive,
        is_superuser: this.isSuperuser,
        password: this.setPassword ? this.password1 : undefined,
      };

      await adminStore.updateUser({
        id: this.user.id,
        user: updatedProfile,
      });
    } finally {
      this.loading = false;
      this.$router.push({
        name: "main-admin-users",
      });
    }
  }

  currentUser(): IUserProfile | null {
    const { id } = this.$router.currentRoute.params;
    return adminStore.adminOneUser(+id);
  }
}
</script>
