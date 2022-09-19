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
            <div class="text-h5">Create User</div>
          </v-card-title>

          <v-card-text>
            <template>
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
                  <!-- password -->
                  <validation-provider
                    v-slot="{ errors }"
                    :debounce="100"
                    name="Password"
                    vid="password1"
                    rules="required"
                  >
                    <v-text-field
                      v-model="password1"
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
                    rules="required|confirmed:password1"
                  >
                    <v-text-field
                      v-model="password2"
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
import { IUserProfileCreate } from "@/interfaces/admin";
import { adminStore } from "@/store";
import { required, confirmed, email } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

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
export default class CreateUser extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  valid: boolean = false;
  fullName: string = "";
  email: string = "";
  isActive: boolean = true;
  isSuperuser: boolean = false;
  password1: string = "";
  password2: string = "";
  showPassword1: boolean = false;
  showPassword2: boolean = false;

  activated() {
    this.onReset();
  }

  onReset() {
    this.password1 = "";
    this.password2 = "";
    this.fullName = "";
    this.email = "";
    this.isActive = true;
    this.isSuperuser = false;
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

    this.loading = true;
    try {
      const updatedProfile: IUserProfileCreate = {
        email: this.email,
        is_active: this.isActive,
        is_superuser: this.isSuperuser,
        password: this.password1,
        full_name: this.fullName,
      };

      await adminStore.createUser(updatedProfile);
    } finally {
      this.loading = false;
      this.$router.push({
        name: "main-admin-users",
      });
    }
  }
}
</script>
