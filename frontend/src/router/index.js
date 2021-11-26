import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

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

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
