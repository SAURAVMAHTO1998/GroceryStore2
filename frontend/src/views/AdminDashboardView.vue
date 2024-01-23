<template>
    <div class="dashboard">
        <h1>Admin Dashboard</h1>
        <!-- Category Create Form -->
        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#categoryCreateModal">
            + Add Category
        </button>


        <div v-if="categories.length === 0">
            <p>{{ categories.length }}</p>
            <p>No Product Categories available!</p>
        </div>
        <div v-else class="mb-3">
            <div class="row">
            <div v-for="category in categories" :key="category.category_id" class="card text-dark border-primary col-md-3 mb-3" style="width: 18rem;">
                <div class="card-body">
                    <h5 class="card-title text-primary"> {{ category.name }} </h5>

                    <div v-for="product in products.filter(s => s.category_id == category.category_id)" :key="product.product_id">
                        <ProductEditModal :product="product" />

                        <button type="button" class="btn btn-secondary" data-bs-toggle="modal"
                            :data-bs-target="'#productEditModal' + product.product_id">
                            Product id: {{ product.product_id }}
                        </button>
                    </div>

                    <CategoryEditModal :category="category" />
                    <ProductCreateModal :category="category" />

                    <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                        :data-bs-target="'#productsCreateModal' + category.category_id">
                        + Add Products
                    </button>

                </div>
                <div class="card-footer">
                    <!-- Category Edit and Delete Buttons -->
                    <button @click="deleteCategory(category.category_id)" class="btn btn-danger">Delete Category</button>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                        :data-bs-target="'#categoryEditModal' + category.category_id">
                        Edit
                    </button>
                </div>
            </div>
            </div>
        </div>
        
        <CategoryCreateModal/>
    </div>
</template>
  
<script>
import ProductCreateModal from "@/components/ProductCreateModal.vue";
import CategoryCreateModal from "@/components/CategoryCreateModal.vue";
import CategoryEditModal from "@/components/CategoryEditModal.vue";
import ProductEditModal from "@/components/ProductEditModal.vue";

import Server from "@/Server";

export default {
    name: "AdminDashboardView",
    data() {
        return {
            categories: [],
            products: [],
        };
    },
    methods: {
        fetchCategories() {
            Server().get('/category/get')
                .then(response => {
                    this.categories = response.data.categories;
                    // console.log("cat aya");
                    console.log("All Categories:", this.categories);
                    console.log("size ",this.categories.length);
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in fetching Categories");
                });
        },
        fetchProducts() {
            Server().get('/product/get')
                .then(response => {
                    this.products = response.data.products;
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in fetching products");
                });
        },
        deleteCategory(categoryID) {
            Server().post(`/category/delete`, { category_id: categoryID })
                .then(response => {
                    console.log(response);
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in deleting category");
                });
        },
        exportCSV(categoryID) {
            Server().post(`/export`, { category_id: categoryID })
                .then(response => {

                    setTimeout(this.checkCSV(response.data.msg), 3000);
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in exporting csv");
                });
        },
        checkCSV(id) {
            Server().post(`/export/status`, { task_id: id })
                .then(response => {
                    alert(response.data.msg);
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in checking csv");
                });
        }
    },
    created() {
        this.fetchCategories();
        this.fetchProducts();
    },
    components: {CategoryCreateModal, ProductCreateModal, CategoryEditModal, ProductEditModal }
};
</script>



<style scoped>
.btn {
    margin: 5px;
    padding: 10px;
}

.card {
    margin: 10px;
    padding: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.card-body {
    border-radius: 10px;
    margin: 10px;
    padding: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}
</style>