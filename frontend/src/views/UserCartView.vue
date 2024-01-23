<template>
    <div class="cart">
        <div class="container">
            <div v-if="cart.length === 0">
                <p>No cart available.</p>
                <router-link to="/products" class="btn btn-success">Add Now!</router-link>
            </div>
            <div v-else>
                <table class="table">
                <thead>
                    <tr>
                        <th>Action</th>
                        <th>Serial No</th>
                        <th>Product Name</th>
                        <th>Quantity</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in cart" :key="index">
                        <td>
                            <button @click="deleteItem(item.cart_id)" class="btn btn-danger">Remove</button>
                        </td>
                        <td>{{ index + 1 }}</td>
                        <!-- <td>{{ item.cart_id }}</td> -->
                        <td>{{ item.product_name }}</td>
                        <td>{{ item.quantity }}</td> <!-- Replace 'quantity' with the actual property name from your data -->
                        <td>{{ item.price }}</td>    <!-- Replace 'price' with the actual property name from your data -->
                    </tr>
                    <tr>
                        <td colspan="3" class="text-right"><strong>Total Price:</strong></td>
                        <td>{{ calculateTotalPrice() }}</td>
                    </tr>
                </tbody>
                </table>
                <button @click="checkout" class="btn btn-primary">Checkout</button>
            </div>
        </div>
    </div>
</template>

<script>
import Server from '@/Server';

export default {
    data() {
        return {
            cart: []
        };
    },
    mounted() {
        Server().get('/cart/get')
            .then(response => {
                console.log("cart ",response);
                this.cart = response.data.cart_items;
                
            })
            .catch(error => {
                console.log(error);
                alert("Error in fetching cart");
            });
    },
    methods: {
        calculateTotalPrice() {
            // Calculate the total price based on the prices of items in the cart
            return this.cart.reduce((total, item) => total + item.price, 0);
        },
        deleteItem(cart_id) {
            Server().post(`/cart/delete`, { cart_id: cart_id })
                .then(response => {
                    console.log(response);
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in deleting cart product");
                });
        },
        checkout() {
            // Extract product IDs from the cart
            const productIds = this.cart.map(item => item.product_id);
            console.log("products ",productIds);
            // Send a POST request to create the order
            Server().post('/order/create', { product_ids: productIds })
                .then(response => {
                    console.log(response);
                    alert(response.data.msg);
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in creating order");
                });
            Server().post('/cart/delete_all')
            .then(response => {
                console.log("response ",response);
                this.cart = response.msg;
                
            })
            .catch(error => {
                console.log(error);
                alert("Error in Checkoutt");
            });
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
