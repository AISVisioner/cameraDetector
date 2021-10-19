import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
  },
  {
    path: "/manager/",
    name: "Manager",
    component: () =>
      import(/* webpackChunkName: "manager-page" */ "../views/Manager.vue"), 
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
