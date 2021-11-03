import { createRouter, createWebHistory } from "vue-router";

// routing to a designated endpoint. -> webpackChunkName names js&css files which are saved in backend/static
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
