<template @search-applied="fetchFilteredProducts">
    <div>
        <h2>Products Available
            <!-- <button class="btn btn-primary" type="button" data-bs-toggle="offcanvas" data-bs-target="#filterOffcanvas"
                aria-controls="filterOffcanvas">
                Filter
            </button> -->
        </h2>

        <!-- <FilterComponent @filter-applied="updateFilteredProducts" /> -->
        <div class="container">
            <div v-if="products.length === 0" class="col">
                <br><br>
                <h3>No products found...</h3>
            </div>
            <div class="row" v-else>
                <div v-for="product in products" :key="product.product_id" class="col">
                    <div class="card" style="width: 18rem;">
                        <img class="card-img-top" :src="require('@/assets/' + product.imagePath)" alt="Card image cap"
                            height="250">
                        <div class="card-body">
                            <h5 class="card-title">{{ product.name }}</h5>
                            <p class="card-text">Price {{ product.price }}</p>
                            <p class="card-text">Stock {{ product.stock }}</p>
                            <ProductAddView :product="product"/>
                            <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                                :data-bs-target="'#productAddView' + product.product_id">
                                + Add 
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script>

import ProductAddView from "@/views/ProductAddView.vue";
import Server from '@/Server';
// import FilterComponent from '@/components/FilterComponent.vue';

export default {
    name: 'ProductsView',
    data() {
        return {
            products: [],
            searchTerm: '',
        };
    },
    methods: {
        fetchProducts() {
            Server().get('/product/get')
                .then(response => {
                    this.products = response.data.products;
                    console.log("len",this.products.length);
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in fetching products");
                });
        },
        updateFilteredProducts(filteredProducts) {
            this.products = filteredProducts;
        },
        async fetchFilteredProducts() {
            try {
                const response = await Server().get('/product/get');
                const allProducts = response.data.products;
                this.products = allProducts.filter(product =>
                product.name.toLowerCase().includes(this.searchTerm.toLowerCase())
                );
            } catch (error) {
                console.log(error);
                alert("Error in fetching products");
            }
        }
    },
    mounted() {
        this.fetchProducts();
        this.$parent.$on('search-applied', searchTerm => {
            this.searchTerm = searchTerm;
            this.fetchFilteredProducts();
        });
    }
    ,
    components: {ProductAddView }
    // ,
    // components: {
    //     FilterComponent
    // }
};
</script>
  
<style scoped></style>
  