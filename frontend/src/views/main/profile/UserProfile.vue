<template>
  <v-container fluid>
    <v-card class="ma-3 elevation-10">
      <v-card-title primary-title class="white--text indigo">
        <div class="text-h5">User Profile</div>
      </v-card-title>
      <v-card-text>
        <div class="my-3">
          <div class="subheading secondary--text text--lighten-3">Full Name</div>
          <div
            v-if="userProfile && userProfile.full_name"
            class="title primary--text text--darken-2"
          >
            {{ userProfile.full_name }}
          </div>
          <div v-else class="title primary--text text--darken-2">-----</div>
        </div>
        <div class="my-3">
          <div class="subheading secondary--text text--lighten-3">Email</div>
          <div class="title primary--text text--darken-2">
            {{ userProfile.email }}
          </div>
        </div>
        <div class="my-3">
          <div class="subheading secondary--text text--lighten-3">Access Role</div>
          <div class="title primary--text text--darken-2">
            {{ userProfile.is_superuser ? "Admin" : "User" }}
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="goToPassword">Change Password</v-btn>
        <v-btn @click="goToAccess">Show Access</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mainStore } from "@/store";
import { IUserProfile } from "@/interfaces/admin";

@Component
export default class UserProfile extends Vue {
  get userProfile(): IUserProfile {
    return mainStore.userProfile;
  }

  goToPassword() {
    this.$router.push({
      name: "main-profile-password",
    });
  }

  goToAccess() {
    this.$router.push({
      name: "main-profile-access",
    });
  }
}
</script>
