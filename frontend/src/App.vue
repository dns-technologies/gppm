<template>
  <div id="app">
    <v-app>
      <v-main v-if="vueIsLoading">
        <v-container fluid fill-height>
          <v-row justify="center">
            <div>
              <div class="text-h5 my-5">Loading...</div>
              <v-progress-circular
                size="100"
                indeterminate
                color="primary"
              ></v-progress-circular>
            </div>
          </v-row>
        </v-container>
      </v-main>
      <router-view v-else />
      <NotificationsManager></NotificationsManager>
    </v-app>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import NotificationsManager from "@/components/NotificationsManager.vue";
import { mainStore } from "@/store";

@Component({
  components: {
    NotificationsManager,
  },
})
export default class App extends Vue {
  get vueIsLoading(): boolean {
    return mainStore.vueIsLoading;
  }

  async created() {
    try {
      await mainStore.checkLoggedIn();
    } finally {
      mainStore.setVueIsLoading(false);
    }
  }
}
</script>


<style>
/* Используется для запрещения редактирования модальных форм */
.no-click {
  pointer-events: none;
}
</style>
