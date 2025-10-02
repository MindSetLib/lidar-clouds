module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  plugins: ["@typescript-eslint", "prettier"],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/vue3-recommended',
    'prettier',
  ],
  parser: "vue-eslint-parser",
  parserOptions: {
    "parser": "@typescript-eslint/parser"
  },
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  rules: {
    'vue/multi-word-component-names': 0,
    'vue/require-default-prop': 0,
    'prettier/prettier': 'error'
  },
}