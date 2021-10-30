<template>
    <div>
        <h1>Logged in as: {{ String(requestUser) }}</h1>
        <b-table striped hover :items="visitors"></b-table>
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
</style>