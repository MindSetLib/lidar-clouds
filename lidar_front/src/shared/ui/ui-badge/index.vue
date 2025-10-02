<template>
  <span class="badge">
    <slot />
  </span>
</template>
<style lang="scss" scoped>
.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 0.375rem;
  background-color: rgb(250 204 21 / 0.1);
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 500;
  color: rgb(234 179 8);

  /* inset-ring inset-ring-yellow-400/20 */
  box-shadow:
      inset 0 0 0 1px rgb(250 204 21 / 0.2),
      inset 0 2px 0 0 rgb(255 255 255 / 0.05),
      inset 0 1px 0 0 rgb(255 255 255 / 0.1);
}

/* Альтернативный вариант с border для inset-ring */
.badge-alternative {
  display: inline-flex;
  align-items: center;
  border-radius: 0.375rem;
  background-color: rgb(250 204 21 / 0.1);
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 500;
  color: rgb(234 179 8);
  border: 1px solid rgb(250 204 21 / 0.2);
  position: relative;
}

.badge-alternative::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 0.375rem;
  box-shadow:
      inset 0 1px 2px rgb(255 255 255 / 0.1),
      inset 0 -1px 1px rgb(0 0 0 / 0.1);
  pointer-events: none;
}
</style>