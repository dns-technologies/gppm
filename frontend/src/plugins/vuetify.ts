import "@mdi/font/css/materialdesignicons.css";
import Vue from "vue";
import Vuetify from "vuetify/lib";

/* 
  Preload components for bypass the warning:
    [mini-css-extract-plugin] Conflicting order.

  For more, look: https://stackoverflow.com/questions/64252325/conflict-order-when-compiling-vue-project
*/

Vue.use(Vuetify);

const opts: any = {
  icons: {
    iconfont: "mdi",
  },
}

export default new Vuetify(opts);