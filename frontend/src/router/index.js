import { createRouter, createWebHistory } from "vue-router";

// ルーター機能で指定されたエンドポイントに移動。→webpackChunkNameでbackend/staticに保存されるjs&cssファイルの名前を指定。
const routes = [
  {
    path: "/",
    name: "home",
    component: () =>
      import(/* webpackChunkName: "home-page" */ "../views/Home.vue"),
    props: true
  },
  {
    path: "/:catchAll(.*)",
    name: "page-not-found",
    component:  () =>
    import(/* webpackChunkName: "not-found" */ "../views/NotFound.vue"),
  }
];

const router = createRouter({
  history: createWebHistory("/"),
  routes,
});

export default router;
