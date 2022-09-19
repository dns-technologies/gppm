<template>
  <router-view></router-view>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mainStore, adminStore } from "@/store";
import { IContext } from "@/interfaces/admin";
import _ from "lodash";

const startRouteGuard = async (to, _from, next) => {
  if (mainStore.isLoggedIn) {
    if (to.path === "/login" || to.path === "/") {
      next("/main");
    } else {
      next();
    }
  } else {
    if (to.path !== "/login") {
      next("/login");
    } else {
      next();
    }
  }
};

const initContext = async (): Promise<boolean> => {
  let needRefresh = false;

  if (mainStore.isLoggedIn) {
    needRefresh = await adminStore.getContextsWithDefault();
  }

  return needRefresh;
};

const updateCurrentProfile = async () => {
  await mainStore.checkLoggedIn();
  if (mainStore.isLoggedIn) {
    await mainStore.getUserProfile(false);
  }
};

const updateCurrentAccess = async () => {
  if (!mainStore.isLoggedIn) {
    return;
  }
  if (mainStore.hasAdminAccess) {
    // Администратору и так все доступно
    return;
  }
  await mainStore.loadCurrentAccess();
};

@Component
export default class Start extends Vue {
  async beforeRouteEnter(to, from, next) {
    mainStore.setLoading(true);
    try {
      await updateCurrentProfile();
      await initContext();
      await updateCurrentAccess();
    } finally {
      mainStore.setLoading(false);
      await startRouteGuard(to, from, next);
    }
  }

  async beforeRouteUpdate(to, from, next) {
    mainStore.setLoading(true);
    try {
      await updateCurrentProfile();
      const needRefresh = await initContext();
      if (needRefresh) {
        this.refreshPage();
      } else {
        await updateCurrentAccess();
      }
    } finally {
      mainStore.setLoading(false);
      await startRouteGuard(to, from, next);
    }
  }

  // На случай, если кто-то изменит конекст
  // Ожидаем редирект
  refreshPage() {
    setTimeout(() => {
      this.$router.go(0);
    }, 500);
  }
}
</script>
