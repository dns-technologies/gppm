<template>
  <keep-alive>
    <router-view>
      <!--  Here is the view component that will be cached -->
    </router-view>
  </keep-alive>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Profile extends Vue {}
</script>
