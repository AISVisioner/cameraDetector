<template>
    <v-container fluid>
        <v-app id="inspire">
            <v-card>
                <v-card-title>
                    Visitors
                    <v-spacer></v-spacer>
                    <v-text-field
                        v-model="search"
                        append-icon="mdi-magnify"
                        label="Search"
                        single-line
                        hide-details
                    ></v-text-field>
                </v-card-title>
                <v-data-table
                    dense

                    :headers="headers"
                    :items="visitors"
                    :page.sync="page"
                    :items-per-page="itemsPerPage"
                    :sort-by="['recent_access_at']"
                    :sort-desc="[false, true]"
                    :search="search"

                    loading-text="Loading... Please wait"

                    item-key="id"

                    multi-sort
                    class="elevation-1"
                    
                    hide-default-footer
                    @page-count="pageCount = $event"
                >
                    <template v-slot:item.photo="{ item }">
                    <div class="p-2">
                        <v-img :src="item.photo" :alt="item.name" width="100px" height="100px"></v-img>
                    </div>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-icon
                        small
                        class="mr-2"
                        @click="editItem(item)"
                        >
                        mdi-pencil
                        </v-icon>
                        <v-icon
                        small
                        @click="deleteItem(item)"
                        >
                        mdi-delete
                        </v-icon>
                    </template>
                </v-data-table>

                <v-dialog
                    v-model="dialog"
                    max-width="500px"
                    persistent
                >
                    <v-card>
                    <v-card-title>
                        <span class="text-h5">{{ 'Edit Item' }}</span>
                    </v-card-title>
        
                    <v-card-text>
                        <v-container>
                        <v-row>
                            <v-col
                                md="10"
                            >
                            <v-text-field
                                v-model="editedItem.name"
                                label="name"
                                :rules="[max40chars]"
                                counter
                            ></v-text-field>
                            </v-col>
                        </v-row>
                        </v-container>
                    </v-card-text>
        
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            color="blue darken-1"
                            text
                            @click="close"
                        >
                        Cancel
                        </v-btn>
                        <v-btn
                            color="blue darken-1"
                            text
                            @click="save"
                        >
                        Save
                        </v-btn>
                    </v-card-actions>
                    </v-card>
                </v-dialog>

                <v-dialog v-model="dialogDelete" max-width="500px" persistent>
                    <v-card>
                    <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
                        <v-btn color="blue darken-1" text @click="deleteItemConfirm">OK</v-btn>
                        <v-spacer></v-spacer>
                    </v-card-actions>
                    </v-card>
                </v-dialog>

                <div class="text-center pt-2">
                    <v-pagination
                        v-model="page"
                        :length="pageCount"
                    ></v-pagination>
                    <v-text-field
                        class="pl-12 pr-12"
                        :value="itemsPerPage"
                        label="Items per page"
                        type="number"
                        min="-1"
                        max="15"
                        @input="itemsPerPage = parseInt($event, 10)"
                    ></v-text-field>
                </div>
            </v-card>
        </v-app>
    </v-container>
</template>

<script>
import { axios } from "@/common/api.service.js";
export default {
    name: "Manager",
    props: {
        requestUser: {type: Object, required: true},
    },
    data() {
        return {
            // requestUser: window.localStorage.getItem("username"),
            // requestUser: null,
            visitors: [],
            next: null,
            // loadingVisitors: false,

            dialog: false,
            dialogDelete: false,

            page: 1,
            pageCount: 0,
            itemsPerPage: 10,

            search: '',

            headers: 
            [
                { text: 'id', value: 'id', align: 'start', sortable: false },
                { text: 'name', value: 'name' },
                { text: 'photo', value: 'photo', sortable: false, filterable: false,},
                { text: 'visits_count', value: 'visits_count' },
                { text: 'recent_access_at', value: 'recent_access_at' },
                { text: 'created_at', value: 'created_at' },
                { text: 'updated_at', value: 'updated_at' },
                { text: 'Actions', value: 'actions', sortable: false },
            ],
            max40chars: v => v.length <= 40 || 'Input too long!',
            
            editedIndex: -1,
            editedItem: { name: '' },
        };
    },
    watch: {
        dialog (val) {
            val || this.close()
        },
        dialogDelete (val) {
            val || this.closeDelete()
        },
    },
    methods: {
        async getToken() {
            // get a token to access REST API
            let endpont = process.env.VUE_APP_TOKENURL;
            try {
                const data = {username: process.env.VUE_APP_USERNAME, password: process.env.VUE_APP_PASSWORD};
                const response = await axios.post(endpont, data);
                const requestAuthtoken = response.data["auth_token"];
                window.localStorage.setItem("auth_token", requestAuthtoken);
                // console.log('auth_token', window.localStorage.getItem("auth_token"));
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
                // console.log('visitors', this.visitors);
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
        editItem (item) {
            this.editedIndex = this.visitors.indexOf(item)
            this.editedItem = Object.assign({}, item)
            this.dialog = true
        },
        deleteItem (item) {
            this.editedIndex = this.visitors.indexOf(item)
            this.editedItem = Object.assign({}, item)
            this.dialogDelete = true
        },
        async deleteItemConfirm () {
            const headers = {"Authorization": `Token ${window.localStorage.getItem("auth_token")}`};
            let endpoint = `${process.env.VUE_APP_VISITORSURL}${this.editedItem.id}/`;
            const data = {
                id: this.editedItem.id,
            }
            try {
                await axios.delete(endpoint, data, {headers});
                // console.log(response.status)
                this.visitors.splice(this.editedIndex, 1)
            } catch (error) {
                console.log(error.response.status)
                if (error.response.status===403 && error.response.statusText==="Forbidden")
                    alert('Forbidden access. You are not a superuser.')
            }
            this.closeDelete()
        },
        close () {
            this.dialog = false
            this.$nextTick(() => {
                this.editedItem = Object.assign({}, this.defaultItem)
                this.editedIndex = -1
            })
        },
        closeDelete () {
            this.dialogDelete = false
            this.$nextTick(() => {
                this.editedItem = Object.assign({}, this.defaultItem)
                this.editedIndex = -1
            })
        },
        save () {
            if (this.editedIndex > -1) {
                Object.assign(this.visitors[this.editedIndex], this.editedItem)
                const headers = {"Authorization": `Token ${window.localStorage.getItem("auth_token")}`};
                let endpoint = `${process.env.VUE_APP_VISITORSURL}${this.editedItem.id}/`;
                const data = {
                    name: this.editedItem.name,
                }
                try {
                    axios.patch(endpoint, data, {headers});
                } catch (error) {
                    console.log(error.response)
                    alert(error.response)
                }
            } else {
                this.visitors.push(this.editedItem)
            }
            this.close()
        },
    },
    created() {
        document.title = "Manager";
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