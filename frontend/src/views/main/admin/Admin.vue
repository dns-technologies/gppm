<template>
  <keep-alive>
    <router-view>
      <!--  Here is the view component that will be cached -->
    </router-view>
  </keep-alive>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mainStore } from "@/store";

const routeGuardAdmin = async (_to, _from, next) => {
  if (!mainStore.hasAdminAccess) {
    next("/main");
  } else {
    next();
  }
};

@Component
export default class Admin extends Vue {
  beforeRouteEnter(to, from, next) {
    routeGuardAdmin(to, from, next);
  }

  beforeRouteUpdate(to, from, next) {
    routeGuardAdmin(to, from, next);
  }
}
</script>
