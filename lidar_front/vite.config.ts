import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0"
  },
  css: {
    preprocessorOptions: {
      scss: {
        /* Для устранения предупреждений консоли:
        * Deprecation Warning [legacy-js-api]: The legacy JS API is deprecated and will be removed in Dart Sass 2.0.0.
        * More info: https://sass-lang.com/d/legacy-js-api
        */
        api: 'modern-compiler' // or "modern"
      }
    }
  }
});
