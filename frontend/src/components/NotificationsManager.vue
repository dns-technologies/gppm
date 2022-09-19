<template>
  <v-snackbar v-model="show" :color="currentNotificationColor" height="60">
    <v-progress-circular v-show="showProgress" class="ma-2" indeterminate>
    </v-progress-circular>
    {{ currentNotificationContent }}

    <template v-slot:action="{ attrs }">
      <v-btn v-bind="attrs" text @click.native="close"> Close </v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts">
import { Vue, Component, Watch } from "vue-property-decorator";
import { IAppNotification } from "@/interfaces/admin";
import { mainStore } from "@/store";

@Component
export default class NotificationsManager extends Vue {
  show: boolean = false;
  text: string = "";
  showProgress: boolean = false;
  currentNotification: IAppNotification | false = false;

  async hide() {
    this.show = false;
    await new Promise<void>((resolve, _reject) => setTimeout(() => resolve(), 500));
  }

  async close() {
    await this.hide();
    await this.removeCurrentNotification();
  }

  async removeCurrentNotification() {
    if (this.currentNotification) {
      mainStore.removeNotification(this.currentNotification);
    }
  }

  get firstNotification(): IAppNotification | false {
    return mainStore.firstNotification;
  }

  async setNotification(notification: IAppNotification | false) {
    if (this.show) {
      await this.hide();
    }
    if (notification) {
      this.currentNotification = notification;
      this.showProgress = notification.showProgress || false;
      this.show = true;
    } else {
      this.currentNotification = false;
    }
  }

  @Watch("firstNotification")
  async onNotificationChange(newNotification: IAppNotification | false) {
    if (newNotification !== this.currentNotification) {
      await this.setNotification(newNotification);
      if (newNotification) {
        mainStore.removeNotificationDelayed({
          notification: newNotification,
          timeout: 6500,
        });
      }
    }
  }

  get currentNotificationContent() {
    return (this.currentNotification && this.currentNotification.content) || "";
  }

  get currentNotificationColor() {
    return (this.currentNotification && this.currentNotification.color) || "info";
  }
}
</script>
