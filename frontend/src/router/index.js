import Vue from "vue";
import VueRouter from "vue-router";
import HomeView from "../views/HomeView.vue";
import ProductsView from "../views/ProductsView.vue";
import LoginView from "../views/LoginView.vue";
import SignupView from "../views/SignupView.vue";
import AdminDashboardView from "../views/AdminDashboardView.vue";
import UserCartView from "../views/UserCartView.vue";
import UserOrderView from "../views/UserOrderView.vue";
import OrderDetailsView from "../views/OrderDetailsView.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/products",
    name: "products",
    component: ProductsView,
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/signup",
    name: "signup",
    component: SignupView,
  },
  {
    path: "/admindashboard",
    name: "admindashboard",
    component: AdminDashboardView,
    meta: {requiresAuth: true,  requiresAdmin: true },
  },
  {
    path: "/mycart",
    name: "cart",
    component: UserCartView,
    meta: {requiresAuth: true},
  },
  {
    path: "/myorders",
    name: "orders",
    component: UserOrderView,
    meta: {requiresAuth: true},
  }, {
    path: '/order/:orderId',
    name: 'order-details',
    component: OrderDetailsView,
    props: true, // Pass route params as props to the component
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});


router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  const isAdmin = localStorage.getItem('isAdmin');

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'login' }); 
    } else if (to.matched.some(record => record.meta.requiresAdmin) && isAdmin == null) {
      next({ name: 'home' }); 
    } else {
      next(); 
    }
  } else {
    next(); 
  }
});

export default router;
