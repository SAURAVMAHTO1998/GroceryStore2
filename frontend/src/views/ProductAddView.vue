
  
<template>
    <div class="modal fade" :id="'productAddView' + product.product_id" tabindex="-1"
        :aria-labelledby="'productAddViewLabel' + product.product_id" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" :id="'productAddViewLabel' + product.product_id">Add Products for {{ product.name }}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="addProduct" id="productForm">
                        <div class="row mb-3">
                            <label for="quantityInput" class="col-sm-2 col-form-label">Select quantity</label>
                            <div class="col-sm-10">
                                <input type="number" class="form-control" id="quantityInput" v-model="newProduct.quantity">
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
    name: "ProductAddView",
    props: {
        product: Object,
    },
    data() {
        return {
            newProduct: {
                product_id: this.product.product_id,
                quantity: ''
            }
        };
    },
    methods: {
        addProduct() {
            // console.log("detail ",this.newProduct)
            Server().post('/addtocart', this.newProduct)
                .then((response) => {
                    console.log(response);
                    alert(response.data.status);
                    window.location.reload();
                    this.newProduct.quantity = '';
                })
                .catch((error) => {
                    console.log(error);
                    alert("Error in creating product");
                });
        },
        closeModal() {
            window.location.reload();
        },
    }
};
</script>