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
                        <th>created_at</th>
                        <th>updated_at</th>
                        <th>recent_access_at</th>
                    </tr>
                </thead>
                <tr v-for="visitors in visitors" v-bind:key="visitors.id">
                    <!-- <td v-for="visitor in visitors" v-bind:key="visitor.id">{{visitor}}</td> -->
                    <td>{{ visitors.id }}</td>
                    <td>{{ visitors.name }}</td>
                    <td><img v-bind:src="visitors.photo" alt="No image to show" width="100" height="100"></td>
                    <td>{{ visitors.visits_count }}</td>
                    <td>{{ visitors.created_at }}</td>
                    <td>{{ visitors.updated_at }}</td>
                    <td>{{ visitors.recent_access_at }}</td>
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
            visitors: [],
            next: null,
            loadingVisitors: false,
        };
    },
    methods: {
        async getVisitors() {
            // make a GET Request to the visitors list endpoint and populate the visitors array
            const headers = {"Authorization": `Token ${window.localStorage.getItem("auth_token")}`}
            let endpoint = "/api/v1/lookup/";
            if (this.next) {
                endpoint = this.next;
            }
            this.loadingVisitors = true;
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
                alert(error.response.statusText);
            }
        },
        checkAuth () {
            if (this.requestUser === null) {
                alert("invalid access");
                this.$router.push({ name: "page-not-found" });
            }
        },

    },
    created() {
        console.log('requestUser(Home):', window.localStorage.getItem("username"));
        document.title = "Manager"
        this.checkAuth();
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