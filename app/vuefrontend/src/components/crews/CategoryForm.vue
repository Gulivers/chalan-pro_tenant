<template>
  <div class="container mt-3">
    <div class="text-center">
      <h3 class="text-warning">Crew Category</h3>
    </div>
    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">{{ formTitle }}</h6>
      </div>
      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label mb-2"
              >Name <span class="text-danger">*</span></label
            >
            <input
              type="text"
              class="form-control"
              v-model.trim="form.name"
              maxlength="100"
              :disabled="isViewMode || submitting"
              required
            />
          </div>
          <div class="d-flex justify-content-center gap-2">
            <button
              type="button"
              class="btn btn-secondary"
              :disabled="submitting"
              @click="goList"
            >
              Cancel
            </button>
            <button
              v-if="!isViewMode"
              type="submit"
              class="btn btn-primary"
              :disabled="submitting"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                role="status"
              ></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-category-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const form = ref({ name: "" });

const formTitle = computed(() => {
  if (isViewMode.value) return "View Category";
  if (isEditMode.value) return "Edit Category";
  return "Add Category";
});

async function loadData() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/categories/${id}/`);
    form.value = { name: data.name || "" };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the category.", "error");
  }
}

function validate() {
  const name = (form.value.name || "").trim();
  if (!name) {
    Swal.fire("Validation", "Name is required.", "warning");
    return false;
  }
  if (name.length > 100) {
    Swal.fire("Validation", "Name must be at most 100 characters.", "warning");
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  try {
    if (id) {
      await axios.patch(`/api/categories/${id}/`, form.value);
      proxy?.notifyToastSuccess?.("Category updated.");
    } else {
      await axios.post("/api/categories/", form.value);
      proxy?.notifyToastSuccess?.("Category created.");
    }
    router.push({ name: "crew-categories" });
  } catch (err) {
    console.error("Save error:", err);
    Swal.fire(
      "Error",
      err.response?.data?.name?.[0] || "Error saving category.",
      "error",
    );
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: "crew-categories" });
}

onMounted(loadData);
</script>
