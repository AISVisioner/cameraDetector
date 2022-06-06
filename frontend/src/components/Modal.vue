<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="695"
    max-height="650"
  >
    <v-card>            
      <div class="text-center">  
        <slot name="body">
          <div class="text-center px-6">
            <h4 class="py-3 name-box">ID: {{ requestUser['username'] }}</h4>
            <p>email: {{ requestUser['email'] }}</p>
            <v-btn
                class="ma-2 mt-0"
                color="orange darken-2"
                dark
                href="/accounts/logout/"
            >
                <v-icon
                    dark
                    left
                >
                mdi-arrow-left
                </v-icon>Logout
            </v-btn>
          </div>
        </slot>
      </div>

      <div class="text-right">
        <slot name="footer">
          <v-spacer />
          <v-btn 
            class="btn-rounded mx-3 mb-3" 
            @click="$emit('update:dialog', false)"
          >Close
          </v-btn>
        </slot>
      </div>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'Modal',
    props: {
      dialog: { type: Boolean, required: true },
      requestUser: { required: true },
    },
  }
</script>


<style scoped>
.btn-vote {
  width: 20%;
  background: #2c2c3f;
  background: -webkit-linear-gradient(to right, #596166, #47474b);  
  background: linear-gradient(to right, #757c81, #3b3b46);
  color: #fff;
  border: 1px solid #eee;
}
.btn-rounded {
  border-radius: 20px;
}
.v-card{
  background-image: linear-gradient(-90deg, #e5ebeb, #f8f9ff);
}
.name-box {
  border-bottom: solid 1px ;
}
</style>