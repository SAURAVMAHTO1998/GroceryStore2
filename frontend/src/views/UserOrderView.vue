<template>
    <div class="orders">
        <div class="container">
            <h2>Your Order History</h2>
            <div v-if="orders.length === 0">
                <p>No Orders</p>
                <router-link to="/products" class="btn btn-success">Order Now!</router-link>
            </div>
            <div v-else>
                <table class="table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Date</th>
            <th>Total Price</th>
            <!-- <th>Details</th> -->
          </tr>
        </thead>
        <tbody>
          <tr v-for="(order, index) in orders" :key="index">
            <td>{{ order.order_id }}</td>
            <td>{{ formatDate(order.order_time) }}</td>
            <td>{{ order.total_price }}</td>
            <!-- <td>
              <router-link :to="{ name: 'order-details', params: { orderId: order.order_id }}">View Details</router-link>
            </td> -->
          </tr>
        </tbody>
      </table>
            </div>
        </div>
    </div>
</template>

<script>
import Server from '@/Server';

export default {
    data() {
        return {
            orders: []
        };
    },
    mounted() {
        Server().get('/order/history')
            .then(response => {
                console.log("order ",response);
                this.orders = response.data.orders;
                
            })
            .catch(error => {
                console.log(error);
                alert("Error in fetching order history");
            });
    },
    methods: {
    formatDate(dateString) {
      // Assuming order_time is a string, you may need to adjust this based on your actual data
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    }
  }
};
</script>

<style scoped>
.container {
    padding: 10px;
    margin: 10px;
    width: 50%;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
    align-items: center;
}

.card {
    margin-bottom: 20px;
}
</style>
