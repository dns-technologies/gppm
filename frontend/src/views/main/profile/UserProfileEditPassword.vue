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
            <div class="text-h5">Set Password</div>
          </v-card-title>
          <v-card-text>
            <template>
              <div class="my-3" v-if="userProfile.full_name">
                <div class="subheading secondary--text text--lighten-2">Full Name</div>
                <div class="title primary--text text--darken-2">
                  {{ userProfile.full_name }}
                </div>
              </div>
              <div class="my-3" v-else>
                <div class="subheading secondary--text text--lighten-2">Email</div>
                <div class="title primary--text text--darken-2">
                  {{ userProfile.email }}
                </div>
              </div>

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
import { mainStore } from "@/store";
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
export default class UserProfileEdit extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  password1: string = "";
  password2: string = "";
  showPassword1: boolean = false;
  showPassword2: boolean = false;

  get userProfile(): IUserProfile {
    return mainStore.userProfile;
  }

  onReset() {
    this.password1 = "";
    this.password2 = "";
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
      const updatedProfile: IUserProfileUpdate = {
        password: this.password1,
      };
      await mainStore.updateUserProfile(updatedProfile);
    } finally {
      this.loading = false;
      this.$router.push({
        name: "main-profile-user",
      });
    }
  }

  activated() {
    this.onReset();
  }
}
</script>
