<template>
  <v-main>
    <v-container fluid fill-height>
      <v-row justify="center">
        <v-col cols="8" md="4">
          <validation-observer ref="observer" v-slot="{ invalid }">
            <v-form @keyup.enter="submit" :class="{ 'no-click': loading }">
              <v-card class="elevation-12">
                <v-toolbar dark color="primary" flat>
                  <v-toolbar-title>{{ appName }}</v-toolbar-title>
                  <v-spacer></v-spacer>
                </v-toolbar>
                <v-card-text>
                  <validation-provider rules="required|email" name="Email">
                    <v-text-field
                      v-model="email"
                      prepend-icon="mdi-account"
                      name="email"
                      label="Email"
                      @keyup.enter="submit"
                    ></v-text-field>
                  </validation-provider>
                  <validation-provider rules="required" name="Password">
                    <v-text-field
                      v-model="password"
                      prepend-icon="mdi-lock"
                      name="password"
                      label="Password"
                      :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="showPassword ? 'text' : 'password'"
                      @click:append="showPassword = !showPassword"
                      @keyup.enter="submit"
                    ></v-text-field>
                  </validation-provider>

                  <div v-if="loginError">
                    <v-alert
                      :value="loginError"
                      transition="fade-transition"
                      type="error"
                    >
                      Incorrect email or password
                    </v-alert>
                  </div>
                </v-card-text>
                <v-card-actions>
                  <v-chip outlined disabled> Auth: {{ authProvider }} </v-chip>
                  <v-spacer></v-spacer>
                  <v-btn @click="submit" :disabled="invalid" :loading="loading"
                    >Login</v-btn
                  >
                </v-card-actions>
              </v-card>
            </v-form>
          </validation-observer>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script lang="ts">
import { Component, Vue, Ref } from "vue-property-decorator";
import { appName } from "@/env";
import { mainStore } from "@/store";

import { required, email } from "vee-validate/dist/rules";
import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

// register validation rules
extend("required", { ...required, message: "{_field_} can not be empty" });
extend("email", { ...email, message: "Invalid email address" });

@Component({
  components: {
    ValidationObserver,
    ValidationProvider,
  },
})
export default class Login extends Vue {
  @Ref()
  observer!: InstanceType<typeof ValidationObserver>;

  loading: boolean = false;
  email: string = "";
  password: string = "";
  appName: string = appName;
  showPassword: boolean = false;

  get loginError(): boolean {
    return mainStore.logInError;
  }

  get authProvider(): string {
    return mainStore.authType;
  }

  async mounted() {
    await mainStore.loadAuthProvider();
  }

  async submit() {
    const success = await this.observer.validate();

    if (!success) {
      return;
    }

    this.loading = true;
    try {
      await mainStore.logIn({
        username: this.email,
        password: this.password,
      });
    } finally {
      this.loading = false;
    }
  }
}
</script>
