<template>
  <div class="upload-container">
    <label for="dropzone-file" class="upload-label">
      <div class="upload-content">
        <svg
          class="upload-icon"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 20 16"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
          />
        </svg>
        <p class="upload-text-primary">
          <span class="upload-text-bold">Нажмите для загруки</span> или
          перетащите
        </p>
        <p class="upload-text-secondary">PCD-файл</p>
      </div>
      <input
        id="dropzone-file"
        type="file"
        class="upload-input"
        accept=".pcd"
        @change="(e) => emit('change', e)"
      />
    </label>
  </div>
</template>
<script setup lang="ts">
const emit = defineEmits(["change"]);
</script>
<style scoped lang="scss">
.upload-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 256px;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  background-color: #191919;
  transition:
    background-color 0.2s,
    border-color 0.2s;
}

.upload-label:hover {
  background-color: #1919190f;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 1.25rem;
  padding-bottom: 1.5rem;
}

.upload-icon {
  width: 2rem;
  height: 2rem;
  margin-bottom: 1rem;
  color: #6b7280;
}

.upload-text-primary {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.upload-text-bold {
  font-weight: 600;
}

.upload-text-secondary {
  font-size: 0.75rem;
  color: #6b7280;
}

.upload-input {
  display: none;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .upload-label {
    background-color: #191919;
    border-color: #545454;
  }

  .upload-label:hover {
    background-color: #191919b1;
    border-color: #d6aa06;
  }

  .upload-icon,
  .upload-text-primary,
  .upload-text-secondary {
    color: #9ca3af;
  }

  .upload-label:hover {
    background-color: #191919b1;
  }
}
</style>
