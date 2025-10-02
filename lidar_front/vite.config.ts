import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import {fileURLToPath, URL} from "node:url";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0"
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: ['.js', '.json', '.jsx', '.mjs', '.ts', '.tsx', '.vue']
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
