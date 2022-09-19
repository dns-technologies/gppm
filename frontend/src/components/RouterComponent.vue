<template>
  <!--
      https://qdmana.com/2021/07/20210725112529482z.html
      https://vuejs.org/api/built-in-components.html
      https://medium.com/chekiprice/caching-routes-in-vuejs-using-keep-alive-advanced-guide-e399839f2673
      https://russianblogs.com/article/31361510651/
    -->
  <keep-alive>
    <router-view>
      <!--  Here is the view component that will be cached -->
    </router-view>
  </keep-alive>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class RouterComponent extends Vue {}
</script>
