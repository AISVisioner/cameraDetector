<template>
    <div>
        <h1>Logged in as: {{ String(requestUser) }}</h1>
        <div class="container">
        <v-app id="inspire">
        <v-data-table
            v-model="selected"
            :headers="headers"
            :items="visitors"
            :single-select="singleSelect"
            item-key="id"
            show-select
            class="elevation-1"
        >
            <template v-slot:top>
                <v-switch
                v-model="singleSelect"
                label="Single select"
                class="pa-3"
                ></v-switch>
            </template>
            <template v-slot:item.name="{ item }">
                <v-edit-dialog
                    :return-value.sync="item.name"
                    large
                    persistent
                    @save="save(item)"
                    @cancel="cancel"
                    @open="open"
                    @close="close"
                > {{ item.name }}
                    <template v-slot:input>
                        <v-text-field
                            v-model="item.name"
                            :rules="[max40chars]"
                            label="Edit"
                            single-line
                            counter
                            autofocus
                        ></v-text-field>
                    </template>
                </v-edit-dialog>
            </template>
            <template v-slot:item.photo="{ item }">
            <div class="p-2">
                <v-img :src="item.photo" :alt="item.name" width="100px" height="100px"></v-img>
            </div>
            </template>
        </v-data-table>
        <div>
            <v-btn color="primary" @click="deleteItem">Delete</v-btn>
        </div>
        </v-app>
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
            singleSelected: false,
            selected: [],
            headers: 
            [
                { text: 'id', value: 'id', align: 'start', sortable: false },
                { text: 'name', value: 'name' },
                { text: 'photo', value: 'photo', sortable: false },
                { text: 'visits_count', value: 'visits_count' },
                { text: 'recent_access_at', value: 'recent_access_at' },
                { text: 'created_at', value: 'created_at' },
                { text: 'updated_at', value: 'updated_at' },
            ],
            max40chars: v => v.length <= 40 || 'Input too long!',
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
        save (item) {
            const headers = {"Authorization": `Token ${window.localStorage.getItem("auth_token")}`};
            let endpoint = `${process.env.VUE_APP_VISITORSURL}${item.id}/`;
            const data = {
                name: item.name,
            }
            try {
                axios.patch(endpoint, data, {headers});
            } catch (error) {
                console.log(error.response)
                alert(error.response)
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