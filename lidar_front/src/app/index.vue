<script setup lang="ts">
import { useRoute } from "vue-router";
import { Routing } from "../pages";

const route = useRoute();
</script>

<template>
  <div class="app">
    <main>
      <Routing />
    </main>
  </div>
</template>

<style>
@import "./style.scss";
</style>
