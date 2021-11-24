<template>
    <div>
        <h1>Logged in as: {{ String(requestUser) }}</h1>
        <div class="container">
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>id</th>
                        <th>name</th>
                        <th>photo</th>
                        <th>visits_count</th>
                        <th>recent_access_at</th>
                        <th>created_at</th>
                        <th>updated_at</th>
                    </tr>
                </thead>
                <tr v-for="visitors in visitors" v-bind:key="visitors.id">
                    <td>{{ visitors.id }}</td>
                    <td>{{ visitors.name }}</td>
                    <td><img v-bind:src="visitors.photo" alt="No image to show" width="100" height="100"></td>
                    <td>{{ visitors.visits_count }}</td>
                    <td>{{ visitors.recent_access_at }}</td>
                    <td>{{ visitors.created_at }}</td>
                    <td>{{ visitors.updated_at }}</td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script>
import { axios } from "@/common/api.service.js";
export default {
    name: "Manager",
    data() {
        return {
            requestUser: window.localStorage.getItem("username"),
            // requestUser: null,
            visitors: [],
            next: null,
            loadingVisitors: false,
        };
    },
    methods: {
        checkAuth () {
            // check if a current user is authorized
            if (this.requestUser === null) {
                alert("invalid access");
                window.location.href = process.env.VUE_APP_LOGINPAGE
                // this.$router.push({ name: "page-not-found" });
                this.$router.push(process.env.VUE_APP_LOGINPAGE);
            }
        },
        async setUserInfo() {
            // add the username of the current user to localStorage
            try {
                const response = await axios.get(process.env.VUE_APP_USERINFOURL);
                const requestUser = response.data["username"];
                window.localStorage.setItem("username", requestUser);
                console.log('requestUser(Home):', window.localStorage.getItem("username"));
            } catch (error) {
                console.log(error.response);
                console.log(this.requestUser)
                alert(error.response.statusText);
            }
        },
        
        async getToken() {
            // get a token to access REST API
            let endpont = process.env.VUE_APP_TOKENURL;
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
        async getVisitors() {
            // make a GET Request to the visitors list endpoint and populate the visitors array
            await new Promise(r => setTimeout(r, 500));
            const headers = {"Authorization": `Token ${window.localStorage.getItem("auth_token")}`}
            let endpoint = process.env.VUE_APP_VISITORSURL;
            if (this.next) { // for future purpose
                endpoint = this.next;
            }
            this.loadingVisitors = true; // for future purpose
            // get all the visitors with REST API
            try {
                const response = await axios.get(endpoint, {headers});
                this.visitors.push(...response.data);
                console.log('visitors', this.visitors);
                this.loadingVisitors = false;
                if (response.data.next) {
                    this.next = response.data.next
                } else {
                    this.next = null;
                }
            } catch (error) {
                console.log(error.response);
                alert(error.response);
            }
        },
    },
    created() {
        document.title = "Manager";
        this.setUserInfo();
        this.checkAuth();
        this.getToken();
        this.getVisitors();
    },
}
</script>

<style scoped>
div {
  text-align: center;
}
table, th, td {
  border: 1px solid black;
}
</style>