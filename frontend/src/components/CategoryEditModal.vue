<template>
    <div class="modal fade" :id="'categoryEditModal' + category.category_id" tabindex="-1"
        :aria-labelledby="'categoryEditModalLabel' + category.category_id" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" :id="'categoryEditModalLabel' + category.category_id">Edit category</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="editcategory" id="categoryEditForm">
                        <div class="row mb-3">
                            <label for="categoryNameEditInput" class="col-sm-2 col-form-label">Category Name</label>
                            <div class="col-sm-10">
                                <input type="text" class="form-control" id="categoryNameEditInput" v-model="editedCategory.name">
                            </div>
                        </div>
                        <!-- <div class="row mb-3">
                            <label for="categoryLocationEditInput" class="col-sm-2 col-form-label">Category Location</label>
                            <div class="col-sm-10">
                                <select class="form-select" id="categoryLocationEditInput" v-model="editedCategory.location">
                                    <option value="Chennai">Chennai</option>
                                    <option value="Bangalore">Bangalore</option>
                                    <option value="Kochi">Kochi</option>
                                </select>
                            </div>
                        </div> -->
                        <button type="submit" class="btn btn-primary" name="submit">Edit Category</button>
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
    name: 'CategoryEditModal',
    props: {
        category: Object,
    },
    data() {
        return {
            editedCategory: {
                category_id: this.category.category_id,
                name: this.category.name
            },
        };
    },
    methods: {
        editcategory() {
            console.log("id ",this.editedCategory.category_id)
            Server().post(`/category/update`, this.editedCategory)
                .then(response => {
                    console.log(response);
                    alert(response.data.msg);
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in editing category");
                });
        },
        closeModal() {
            window.location.reload();
        },
    }
};
</script>
  