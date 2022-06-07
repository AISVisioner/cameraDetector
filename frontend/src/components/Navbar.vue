<template>
  <div>
    <v-app-bar
      color="deep-purple lighten-1"
      dense
      dark
    >
      <v-toolbar-title class="font-weight-black">{{ appTitle }}</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn
        icon
        @click="openModal()"
      >
        <v-icon>mdi-account</v-icon>
      </v-btn>
    </v-app-bar>
    <modal
      :dialog.sync="isModal"
      :requestUser="requestUser"
    />
  </div>
</template>

<script>
import Modal from './Modal.vue';
// import { axios } from "@/common/api.service.js";
export default {
  name: "NavbarComponent",
  props: {
    requestUser: { required: true },
  },
  components: {
    Modal
  },
  data() {
    return {
      appTitle: 'Kiosk',
      isModal: false,
    };
  },
  methods: {
    openModal() {
      this.isModal = true;
      // console.log(this.isModal)
    },
    closeModal() {
      this.isModal = false;
    }
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