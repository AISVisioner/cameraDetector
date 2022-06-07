<template>
  <div id="app">
    <v-app id="inspire">
      <div id="nav">
        <NavbarComponent :requestUser="requestUser" />
        <router-view :requestUser="requestUser" />
      </div>
    </v-app>
  </div>
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
      requestUser: null,
    };
  },
  methods: {
    async setUserInfo() {
        // add the username of the current user to localStorage
        try {
            const response = await axios.get(process.env.VUE_APP_USERINFOURL);
            const requestUser = response.data;
            // window.localStorage.setItem("username", requestUser);
            // console.log('requestUser(Home):', window.localStorage.getItem("username"));
            this.requestUser = requestUser;
            this.checkAuth();
        } catch (error) {
            console.log(error.response);
            console.log(this.requestUser)
            alert(error.response.statusText);
        }
    },
    checkAuth () {
        // check if a current user is authorized
        if (this.requestUser === null) {
            alert("invalid access");
            window.location.href = process.env.VUE_APP_LOGINPAGE
            // this.$router.push({ name: "page-not-found" });
            this.$router.push(process.env.VUE_APP_LOGINPAGE);
        }
    },
  },
  created() {
    this.setUserInfo();
  }

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
