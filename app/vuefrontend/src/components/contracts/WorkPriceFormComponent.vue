<template>
    <div class="container">
        <h3 class="text-warning pt-3"><p>Piece Work Prices</p></h3>
        <div class="card shadow mb-4">
            <div class="card-header py-2">
                <h6 class="m-0 font-weight-bold text-primary">{{ isNewPrice ? 'Create' : 'Edit' }} Price</h6>
            </div>
            <div class="card-body">
                <div class="row text-start">
                    <!-- Formulario de edición/creación de precios -->
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="name" class="form-label">Name</label>
                            <input type="text" class="form-control" id="name" v-model="newPrice.name"
                                placeholder="Enter Description" :readonly="isReadOnly">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="trim" class="form-label">Trim</label>
                            <input type="number" class="form-control" id="trim" v-model="newPrice.trim"
                                placeholder="00.00" :readonly="isReadOnly">
                        </div>
                    </div>
                </div>
                <div class="row text-start">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="rough" class="form-label">Rough</label>
                            <input type="number" class="form-control" id="rough" v-model="newPrice.rough"
                                placeholder="00.00" :readonly="isReadOnly">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="unitPrice" class="form-label">Unit Price Type</label>
                            <select class="form-select" id="unitPrice" v-model="newPrice.unit_price" :disabled="isReadOnly">
                                <option value="">Select unit price type</option>
                                <option value="Ea">Ea</option>
                                <option value="Total">Total</option>
                            </select>
                        </div>
                    </div>
                </div>
              <div class="row text-start text-black">
                <div class="col-12 text-start my-3">
                  <h4 class="mb-0">Builders</h4>
                </div>
                <div class="col-lg-6 ms-3 mb-3">
                  <div class="btn-group" role="group" aria-label="Basic outlined example" v-if="!isReadOnly">
                    <button type="button" class="btn btn-sm btn-outline-primary" @click="selectAll">Select All</button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="clearAll">Deselect All</button>
                  </div>
                </div>
              </div>
              <div class="row px-3 text-start mb-3">
                  <div class="form-check form-switch col-xl-3 col-md-4 col-sm-6" v-for="builder in availableBuilders"
                       :key="builder.id">
                    <input class="form-check-input form-primary" type="checkbox" role="switch" :value="builder.id"
                           v-model="selectedChosenBuilders" :disabled="isReadOnly">
                    <label class="form-check-label">{{ builder.name }}</label>
                  </div>
              </div>
                <div class="row">
                    <div class="col" v-if="!isReadOnly">
                        <button class="btn btn-primary" @click="createOrUpdatePrice">Save</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from 'axios';

    export default {
        name: 'WorkPricesFormView',
        data() {
            return {
                newPrice: {
                    name: '',
                    trim: 0,
                    rough: 0,
                    unit_price: '',
                },
                isNewPrice: true,
                availableBuilders: [],
                chosenBuilders: [],
                selectedAvailableBuilders: [],
                selectedChosenBuilders: [],
            };
        },
        computed: {
            isReadOnly() {
                return this.$route.name === 'work-prices-view';
            }
        },
        mounted() {
            this.fetchAvailableBuilders();
            this.fetchPriceToUpdate();
        },
        methods: {
          selectAll(){
            this.selectedChosenBuilders = this.availableBuilders.map(b => b.id);
          },
          clearAll(){
            this.selectedChosenBuilders = [];
          },
            fetchPriceToUpdate() {
                const idToUpdate = this.$route.params.id;
                if (idToUpdate) {
                    this.isNewPrice = false;
                    axios.get(`/api/workprice/${idToUpdate}/`)
                        .then(response => {
                            const editData = response.data;
                            this.newPrice = {
                                name: editData.name,
                                trim: editData.trim,
                                rough: editData.rough,
                                unit_price: editData.unit_price,
                            };
                            this.selectedChosenBuilders = editData.builders;
                            this.updateAvailableBuilders();
                        })
                        .catch(error => {
                            console.error('Error fetching data for editing:', error);
                        });
                }
            },
            fetchAvailableBuilders() {
                axios.get('/api/builder/')
                    .then(response => {
                        this.availableBuilders = response.data;
                        this.updateAvailableBuilders();
                    })
                    .catch(error => {
                        console.error('Error fetching available builders:', error);
                    });
            },
            updateAvailableBuilders() {
                const chosenIds = this.chosenBuilders.map(builder => builder.id);
                this.availableBuilders = this.availableBuilders.filter(builder => !chosenIds.includes(builder.id));
            },
            createOrUpdatePrice() {
                if (this.isReadOnly) return;

                const idToUpdate = this.$route.params.id;
                const url = idToUpdate ? `/api/workprice/${idToUpdate}/` : '/api/workprice/';

                const dataToSend = {
                    ...this.newPrice,
                    builders: this.selectedChosenBuilders
                };

                console.log('Datos enviados:', dataToSend);  

                axios[idToUpdate ? 'put' : 'post'](url, dataToSend)
                    .then(response => {
                        console.log('Price saved successfully:', response.data);
                        this.$router.push('/work-prices');
                    })
                    .catch(error => {
                        console.error('Error saving price:', error);
                    });
            }
        }
    };
</script>
