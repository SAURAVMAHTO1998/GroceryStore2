<template>
    <div class="modal fade" :id="'productEditModal' + product.product_id" tabindex="-1"
        :aria-labelledby="'productEditModalLabel' + product.product_id" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" :id="'productEditModalLabel' + product.product_id">Edit Product {{ product.name }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="editProduct">
                        <div class="row mb-3">
                            <label for="editProductNameInput" class="col-sm-2 col-form-label">Name</label>
                            <div class="col-sm-10">
                                <input type="text" class="form-control" id="editProductNameInput" v-model="editedProduct.name">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="editProductImageInput" class="col-sm-2 col-form-label">Image</label>
                            <div class="col-sm-8">
                                <input type="file" class="form-control" id="editProductImageInput" @change="handleImageChange">
                            </div>
                            <div class="col-sm-2">
                                <!-- Display the file name -->
                                <input type="text" class="form-control" v-model="editedProduct.image_src" readonly>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="editProductPriceInput" class="col-sm-2 col-form-label">Price</label>
                            <div class="col-sm-10">
                                <input type="number" class="form-control" id="editProductPriceInput"
                                    v-model="editedProduct.price">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="editProductStocksInput" class="col-sm-2 col-form-label">Stock</label>
                            <div class="col-sm-10">
                                <input type="number" class="form-control" id="editProductStocksInput"
                                    v-model="editedProduct.stock">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </form>
                    <button @click.stop="deleteProduct(product.product_id)" class="btn btn-danger">Delete Product</button>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script>
import Server from "@/Server";

export default {
    name: "ProductEditModal",
    props: {
        product: Object,
    },
    data() {
        return {
            editedProduct: {
                product_id: this.product.product_id,
                category_id: this.product.category_id,
                name: this.product.name,
                image_src: this.product.image_src,
                price: this.product.price,
                stock: this.product.stock,

            },
        };
    },
    methods: {
        editProduct() {
            Server().post(`/product/update`, this.editedProduct)
                .then(response => {
                    console.log(response);
                    alert(response.data.msg);
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in editing product");
                });
        },
        handleImageChange(event) {
            const file = event.target.files[0];

            if (file) {
        // Create a FileReader
        const reader = new FileReader();

        // Set the callback for when the file is loaded
        reader.onload = (e) => {
            // Set the data URL to the editedProduct.image_src
            this.editedProduct.image_src = e.target.result;
        };

        // Read the file as a data URL
        reader.readAsDataURL(file);
    }
        },
        deleteProduct(productID) {
            Server().post(`/product/delete`, { product_id: productID })
                .then(response => {
                    console.log(response);
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in deleting product");
                });
        },
        closeModal() {
            window.location.reload();
        },
    },
}
</script>
  