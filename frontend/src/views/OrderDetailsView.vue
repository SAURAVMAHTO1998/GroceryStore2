<template>
    <div class="order-details">
      <h2>Order Details</h2>
      <div>
        <p><strong>Order ID:</strong> {{ order.order_id }}</p>
        <p><strong>Date:</strong> {{ formatDate(order.order_time) }}</p>
        <p><strong>Total Price:</strong> {{ order.total_price }}</p>
        
        <h3>Products in Order</h3>
        <ul>
          <li v-for="(product, index) in order.products" :key="index">
            {{ product.name }} - Quantity: {{ product.quantity }} - Price: {{ product.price }}
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import Server from '@/Server';  // Import your API handling module
  
  export default {
    props: {
      orderId: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        order: {},
      };
    },
    mounted() {
      // Fetch order details when the component is mounted
      this.fetchOrderDetails();
    },
    methods: {
      fetchOrderDetails() {
        // Assuming you have an API endpoint to fetch order details by orderId
        // Replace 'YOUR_API_ENDPOINT' with the actual endpoint
        Server().get(`/api/orders/${this.orderId}`)
          .then(response => {
            this.order = response.data;
          })
          .catch(error => {
            console.error('Error fetching order details:', error);
          });
      },
      formatDate(dateString) {
        // Format date as needed
        return new Date(dateString).toLocaleDateString();
      },
    },
  };
  </script>
  
  <style scoped>
  /* Add styles as needed */
  </style>
  