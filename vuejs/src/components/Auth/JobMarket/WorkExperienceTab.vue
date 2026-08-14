<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import axios from 'axios';
import { authUserStore } from '@/stores/authUserStore';

const props = defineProps({
  userId: { type: Number, required: true },
  isOwner: { type: Boolean, default: false },
  highlightId: { type: [Number, String], default: null },
});

const userStore = authUserStore();
const items = ref([]);
const loading = ref(true);
const error = ref(null);
const formOpen = ref(false);
const editingId = ref(null);
const suggestions = ref([]);
const form = ref({
  company_name: '',
  company_id: null,
  employment_type: 'full-time',
  title: '',
  location: '',
  start_date: '',
  end_date: '',
  mode: 'free', // free | linked
});

const employmentTypes = [
  'full-time',
  'part-time',
  'hybrid',
  'outsourcing',
  'collaborator',
];

const myCompanyId = computed(() => userStore.companyId);

const statusLabel = (status) => {
  if (status === 'approved') return 'Approved';
  if (status === 'rejected') return 'Rejected';
  return 'Pending';
};

const canDecide = (row) =>
  row.status === 'pending' &&
  row.company_id != null &&
  myCompanyId.value != null &&
  Number(row.company_id) === Number(myCompanyId.value);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await axios.get(
      `/api/job-market/users/${props.userId}/work-experiences`
    );
    items.value = data;
    await nextTick();
    scrollHighlight();
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Failed to load experience';
  } finally {
    loading.value = false;
  }
}

function scrollHighlight() {
  const id = props.highlightId;
  if (!id) return;
  const el = document.getElementById(`work-exp-${id}`);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function resetForm() {
  editingId.value = null;
  suggestions.value = [];
  form.value = {
    company_name: '',
    company_id: null,
    employment_type: 'full-time',
    title: '',
    location: '',
    start_date: '',
    end_date: '',
    mode: 'free',
  };
}

function openCreate() {
  resetForm();
  formOpen.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  form.value = {
    company_name: row.company_name,
    company_id: row.company_id,
    employment_type: row.employment_type,
    title: row.title,
    location: row.location || '',
    start_date: row.start_date,
    end_date: row.end_date || '',
    mode: row.company_id ? 'linked' : 'free',
  };
  formOpen.value = true;
}

async function searchCompanies() {
  const q = form.value.company_name?.trim();
  if (!q || q.length < 1) {
    suggestions.value = [];
    return;
  }
  try {
    const { data } = await axios.get('/api/job-market/company-suggestions', {
      params: { q, limit: 8 },
    });
    suggestions.value = data;
  } catch {
    suggestions.value = [];
  }
}

function pickCompany(c) {
  form.value.company_id = c.id;
  form.value.company_name = c.display_name;
  form.value.mode = 'linked';
  suggestions.value = [];
}

function clearLinkedCompany() {
  form.value.company_id = null;
  form.value.mode = 'free';
}

async function save() {
  const payload = {
    employment_type: form.value.employment_type,
    title: form.value.title,
    location: form.value.location || null,
    start_date: form.value.start_date,
    end_date: form.value.end_date || null,
  };
  if (form.value.company_id) {
    payload.company_id = form.value.company_id;
  } else if (editingId.value) {
    payload.clear_company_id = true;
    payload.company_name = form.value.company_name;
  } else {
    payload.company_name = form.value.company_name;
  }
  try {
    if (editingId.value) {
      await axios.patch(
        `/api/job-market/me/work-experiences/${editingId.value}`,
        payload
      );
    } else {
      await axios.post('/api/job-market/me/work-experiences', payload);
    }
    formOpen.value = false;
    resetForm();
    await load();
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Save failed';
  }
}

async function remove(id) {
  if (!confirm('Delete this experience?')) return;
  try {
    await axios.delete(`/api/job-market/me/work-experiences/${id}`);
    await load();
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Delete failed';
  }
}

async function decide(row, action) {
  try {
    await axios.post(
      `/api/job-market/me/company/work-experiences/${row.id}/${action}`
    );
    await load();
  } catch (e) {
    error.value = e?.response?.data?.detail || `${action} failed`;
  }
}

watch(() => props.highlightId, () => nextTick(scrollHighlight));
onMounted(load);
</script>

<template>
  <div class="px-8 py-6 max-w-3xl mx-auto w-full">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">Work experience</h2>
      <button
        v-if="isOwner"
        type="button"
        class="px-4 py-2 bg-black text-white rounded-full text-sm"
        @click="openCreate"
      >
        Add
      </button>
    </div>

    <p v-if="loading" class="text-gray-500">Loading…</p>
    <p v-else-if="error" class="text-red-600 text-sm mb-3">{{ error }}</p>
    <p v-else-if="!items.length" class="text-gray-500">No experience yet.</p>

    <ul v-else class="space-y-4">
      <li
        v-for="row in items"
        :id="`work-exp-${row.id}`"
        :key="row.id"
        class="border-b border-gray-200 pb-4"
        :class="{
          'ring-2 ring-black rounded-lg p-3':
            highlightId != null && Number(highlightId) === Number(row.id),
        }"
      >
        <div class="flex justify-between gap-4">
          <div>
            <p class="font-semibold text-lg">{{ row.title }}</p>
            <p class="text-gray-800">
              {{ row.company_name }} · {{ row.employment_type }}
              <span v-if="row.company_id" class="text-xs text-gray-500"> (on-system)</span>
            </p>
            <p class="text-sm text-gray-600">
              {{ row.start_date }}
              →
              {{ row.end_date || 'Present' }}
              <span v-if="row.location"> · {{ row.location }}</span>
            </p>
            <p class="text-sm mt-1 font-medium">{{ statusLabel(row.status) }}</p>
          </div>
          <div class="flex flex-col gap-2 text-sm shrink-0 items-end">
            <div v-if="isOwner" class="flex gap-2">
              <button type="button" class="underline" @click="openEdit(row)">
                Edit
              </button>
              <button type="button" class="underline text-red-600" @click="remove(row.id)">
                Delete
              </button>
            </div>
            <div v-if="canDecide(row)" class="flex gap-2">
              <button
                type="button"
                class="px-3 py-1 bg-black text-white rounded-full text-xs"
                @click="decide(row, 'approve')"
              >
                Approve
              </button>
              <button
                type="button"
                class="px-3 py-1 border rounded-full text-xs"
                @click="decide(row, 'reject')"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </li>
    </ul>

    <div
      v-if="formOpen"
      class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center"
      @click.self="formOpen = false"
    >
      <form
        class="bg-white rounded-2xl p-6 w-full max-w-md space-y-3"
        @submit.prevent="save"
      >
        <h3 class="text-lg font-bold">
          {{ editingId ? 'Edit experience' : 'Add experience' }}
        </h3>
        <div class="relative">
          <input
            v-model="form.company_name"
            required
            placeholder="Company (type to search)"
            class="w-full border rounded-lg px-3 py-2"
            @input="searchCompanies"
          />
          <ul
            v-if="suggestions.length"
            class="absolute z-10 left-0 right-0 bg-white border rounded-lg mt-1 max-h-40 overflow-auto text-sm"
          >
            <li
              v-for="c in suggestions"
              :key="c.id"
              class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
              @click.prevent="pickCompany(c)"
            >
              {{ c.display_name }}
            </li>
          </ul>
          <p v-if="form.company_id" class="text-xs text-gray-600 mt-1">
            Linked company #{{ form.company_id }}
            <button type="button" class="underline ml-2" @click="clearLinkedCompany">
              Use free-text instead
            </button>
          </p>
        </div>
        <select v-model="form.employment_type" class="w-full border rounded-lg px-3 py-2">
          <option v-for="t in employmentTypes" :key="t" :value="t">{{ t }}</option>
        </select>
        <input
          v-model="form.title"
          required
          placeholder="Title / role"
          class="w-full border rounded-lg px-3 py-2"
        />
        <input
          v-model="form.location"
          placeholder="Location"
          class="w-full border rounded-lg px-3 py-2"
        />
        <label class="block text-sm"
          >Start
          <input v-model="form.start_date" type="date" required class="w-full border rounded-lg px-3 py-2"
        /></label>
        <label class="block text-sm"
          >End (optional)
          <input v-model="form.end_date" type="date" class="w-full border rounded-lg px-3 py-2"
        /></label>
        <div class="flex justify-end gap-2 pt-2">
          <button type="button" class="px-4 py-2" @click="formOpen = false">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-black text-white rounded-full">Save</button>
        </div>
      </form>
    </div>
  </div>
</template>
