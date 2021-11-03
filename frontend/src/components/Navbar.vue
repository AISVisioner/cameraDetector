<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light my-navbar">
    <div class="container">
      <router-link :to="{ name: 'home' }" class="navbar-brand"
        >Kiosk
      </router-link>

      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto">
          <li v-if="requestUser===null" class="nav-item mx-1">
            <a class="btn btn-danger" href="/accounts/login/"
              >Log in
            </a>
          </li>
          <li v-else class="nav-item">
            <a class="btn btn-outline-secondary" href="/accounts/logout/"
              >Log out
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
// import { axios } from "@/common/api.service.js";
export default {
  name: "NavbarComponent",
  props: {
    requestUser: {
        type: String,
    },
  },
};
</script>

<style>
.my-navbar {
  border-bottom: 1px solid #ddd;
}

.navbar-brand {
  font-weight: bold;
  font-size: 150%;
}

.navbar-brand:hover {
  color: #dc3545 !important;
}
</style>