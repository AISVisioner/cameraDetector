<template>
    <div>
        <h1>Logged in as: {{ String(requestUser) }}</h1>
    </div>
</template>

<script>
// import { axios } from "@/common/api.service.js";
export default {
    name: "Manager",
    props: {
        requestUser: {
            type: String,
        },
    },
    methods: {
        checkAuth () {
            if (this.requestUser === null) {
                alert("invalid access");
                this.$router.push({ name: "page-not-found" });
            }
        },
    },
    created() {
        this.checkAuth();
    },
}
</script>

<style scoped>
div {
  text-align: center;
}
</style>