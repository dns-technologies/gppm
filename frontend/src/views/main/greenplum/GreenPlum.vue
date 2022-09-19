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

const routeGuardGreenPlum = async (to, _from, next) => {
  if (!mainStore.hasActiveContext) {
    next("/main");
  } else if (!mainStore.hasAdminAccess && to.path === "/main/greenplum/roles/create") {
    next("/main");
  } else {
    next();
  }
};

@Component
export default class GreenPlum extends Vue {
  beforeRouteEnter(to, from, next) {
    routeGuardGreenPlum(to, from, next);
  }

  beforeRouteUpdate(to, from, next) {
    routeGuardGreenPlum(to, from, next);
  }
}
</script>
