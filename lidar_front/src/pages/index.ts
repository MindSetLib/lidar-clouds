import Routing from "./index.vue";

export const routes = [
  { path: "/", component: () => import("./pcd/index.ts"), name: "Home", },
  { path: "/pcd", component: () => import("./pcd/index.ts"), name: "PCD", }
];

export { Routing };
