import Routing from "./index.vue";

export const routes = [
  { path: "/", component: () => import("./index.vue"), name: "Home", },
  { path: "/pcd", component: () => import("./pcd/index.ts"), name: "PCD", }
];

export { Routing };
