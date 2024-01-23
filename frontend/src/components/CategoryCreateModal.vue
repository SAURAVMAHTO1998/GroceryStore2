<template>
    <div class="modal fade" id="categoryCreateModal" tabindex="-1" aria-labelledby="categoryCreateModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="categoryCreateModalLabel">Create Category</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="createCategory">
                        <div class="row mb-3">
                            <label for="categoryNameInput" class="col-sm-2 col-form-label">Category Name</label>
                            <div class="col-sm-10">
                                <input type="text" class="form-control" id="categoryNameInput" v-model="newCategory.name">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary" name="submit">Create Category</button>
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
    name: "CategoryCreateModal",
    data() {
        return {
            newCategory: {
                name: ''
            }
        };
    },
    methods: {
        createCategory() {
            Server().post('/category/create', this.newCategory)
                .then(response => {
                    console.log(response);
                    alert(response.data.msg);
                    this.newCategory.name = '';
                    window.location.reload();
                })
                .catch(error => {
                    console.log(error);
                    alert("Error in creating category");
                });
        },
        closeModal() {
            window.location.reload();
        },
    }
};
</script>