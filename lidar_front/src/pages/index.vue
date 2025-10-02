<template>
  <RouterView v-slot="{ Component, route }">
    <template v-if="Component">
      <Transition :name="getTransitionName(route.meta)">
        <Suspense>
          <template #default>
            <component :is="Component" />
          </template>
        </Suspense>
      </Transition>
    </template>
    <template v-else>
      <div
        style="
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        "
      >
        <input type="file" />
      </div>
    </template>
  </RouterView>
</template>
<script setup lang="ts">
import { RouteMeta, RouterView, useRouter } from "vue-router";
import { ref } from "vue";

const router = useRouter();
const isShowLoader = ref(false);

const getTransitionName = (transitionMeta: RouteMeta) => {
  if (
      transitionMeta &&
      typeof transitionMeta === "object" &&
      transitionMeta.transition &&
      typeof transitionMeta.transition === "string"
  ) {
    return transitionMeta.transition;
  }
  return "fade";
};

router.beforeEach(() => {
  isShowLoader.value = true;
});
router.afterEach(() => {
  isShowLoader.value = false;
});
</script>
