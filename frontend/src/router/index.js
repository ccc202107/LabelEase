import Vue from "vue";
import Router from "vue-router";
import LabelAnomaly from "@/views/LabelAnomaly";
import LabelRootCause from "@/views/labelrootcause";
Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      name: "LabelAnomaly",
      component: LabelAnomaly
    },
    {
      path: "/labelrootcause",
      name: "LabelRootCause",
      component: LabelRootCause
    }
  ]
});
