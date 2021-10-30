<template>
  <div id="nav">
    <NavbarComponent />
  </div>
  <router-view />
</template>

<script>
import { axios } from "@/common/api.service.js";
import NavbarComponent from "@/components/Navbar.vue";
export default {
  name: "App",
  components: {
    NavbarComponent,
  },
  methods: {
    async getToken() {
      let endpont = "/auth/token/login/";
      try {
        const data = {username: process.env.VUE_APP_USERNAME, password: process.env.VUE_APP_PASSWORD};
        const response = await axios.post(endpont, data);
        const requestAuthtoken = response.data["auth_token"];
        window.localStorage.setItem("auth_token", requestAuthtoken);
        console.log('auth_token', window.localStorage.getItem("auth_token"));
      } catch (error) {
        console.log(error.response);
        alert(error.response.statusText);
      }
    },
    async setUserInfo() {
      // add the username of the current user to localStorage
      try {
        const response = await axios.get("/auth/users/me/");
        const requestUser = response.data["username"];
        window.localStorage.setItem("username", requestUser);
        // this.requestUser = window.localStorage.getItem("username");
        console.log('requestUser:', window.localStorage.getItem("username"));
      } catch (error) {
        console.log(error.response);
        console.log(this.requestUser)
        alert(error.response.statusText);
      }
    },
  },
  created() {
    this.getToken();
    this.setUserInfo();
  },
};
</script>

<style>
body {
  font-family: 'Noto Sans JP', sans-serif;
  font-weight: 300;
}

.btn:focus {
  box-shadow: none !important;
}
</style>
