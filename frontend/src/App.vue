<template>
  <div id="nav">
    <NavbarComponent :requestUser="requestUser"/>
  </div>
  <router-view :requestUser="requestUser"/>
</template>

<script>
import { axios } from "@/common/api.service.js";
import NavbarComponent from "@/components/Navbar.vue";
export default {
  name: "App",
  components: {
    NavbarComponent,
  },
  data() {
    return {
      requestUser: null, // propsを使わない方が安全か？
    };
  },
  methods: {
    async setUserInfo() {
      // add the username of the current user to localStorage
      try {
        const response = await axios.get("/auth/users/me/");
        const requestUser = response.data["username"];
        window.localStorage.setItem("username", requestUser);
        this.requestUser = window.localStorage.getItem("username");
        console.log(this.requestUser)
      } catch (error) {
        console.log(error.response);
        console.log(this.requestUser)
        // alert(error.response.statusText);
      }
    },
  },
  created() {
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
