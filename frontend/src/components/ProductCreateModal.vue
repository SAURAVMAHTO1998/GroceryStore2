
  
<template>
    <div class="modal fade" :id="'productsCreateModal' + category.category_id" tabindex="-1"
        :aria-labelledby="'productCreateModalLabel' + category.category_id" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" :id="'productCreateModalLabel' + category.category_id">Add Products for {{ category.name }}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="addProduct" id="productForm">
                        <div class="row mb-3">
                            <label for="productNameInput" class="col-sm-2 col-form-label">Name</label>
                            <div class="col-sm-10">
                                <input type="text" class="form-control" id="productNameInput" v-model="newProduct.name">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="productImageInput" class="col-sm-2 col-form-label">Image</label>
                            <div class="col-sm-10">
                                <input type="file" class="form-control" id="productImageInput" @change="handleImageUpload">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="productPriceInput" class="col-sm-2 col-form-label">Price</label>
                            <div class="col-sm-10">
                                <input type="number" class="form-control" id="productPriceInput"
                                    v-model="newProduct.price">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="stockInput" class="col-sm-2 col-form-label">Stock</label>
                            <div class="col-sm-10">
                                <input type="number" class="form-control" id="stockInput" v-model="newProduct.stock">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary" name="submit" value="Add Product">Add Product</button>
                    </form>
                </div>
                <div class="modal-footer">
                    <button @click="closeModal" type="button" class="btn btn-secondary"
                        data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script>
import Server from '@/Server';

export default {
    name: "ProductCreateModal",
    props: {
        category: Object,
    },
    data() {
        return {
            newProduct: {
                category_id: this.category.category_id,
                name: '',
                image_src: null,
                price: '',
                stock: ''
            }
        };
    },
    methods: {
        addProduct() {
            Server().post('/product/create', this.newProduct)
                .then((response) => {
                    console.log(response);
                    alert(response.data.msg);
                    window.location.reload();
                    this.newProduct.name = '';
                    this.newProduct.image_src = null;
                    this.newProduct.price = '';
                    this.newProduct.stock = '';
                })
                .catch((error) => {
                    console.log(error);
                    alert("Error in creating product");
                });
        },
        handleImageUpload(event) {
            const file = event.target.files[0];

            if (file) {
                this.newProduct.image_src = file.name;
            }
        },
        closeModal() {
            window.location.reload();
        },
    }
};
</script>