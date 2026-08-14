<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

const rows = ref([])
const loading = ref(false)
const filters = ref({
  actor_user_id: '',
  action: '',
  target_type: '',
  target_id: '',
  date_from: '',
  date_to: '',
  limit: 50,
  offset: 0,
})

function buildParams() {
  const params = {
    limit: Number(filters.value.limit) || 50,
    offset: Number(filters.value.offset) || 0,
  }
  if (filters.value.actor_user_id) params.actor_user_id = Number(filters.value.actor_user_id)
  if (filters.value.action) params.action = filters.value.action
  if (filters.value.target_type) params.target_type = filters.value.target_type
  if (filters.value.target_id) params.target_id = Number(filters.value.target_id)
  if (filters.value.date_from) params.date_from = new Date(filters.value.date_from).toISOString()
  if (filters.value.date_to) params.date_to = new Date(filters.value.date_to).toISOString()
  return params
}

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/admin/audit', { params: buildParams() })
    rows.value = data
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <form class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm" @submit.prevent="load">
      <label>
        <span class="text-gray-600">Actor user id</span>
        <input v-model="filters.actor_user_id" type="number" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <label>
        <span class="text-gray-600">Action</span>
        <input v-model="filters.action" class="mt-1 w-full border rounded-md px-2 py-1.5" placeholder="role_assign" />
      </label>
      <label>
        <span class="text-gray-600">Target type</span>
        <input v-model="filters.target_type" class="mt-1 w-full border rounded-md px-2 py-1.5" placeholder="user" />
      </label>
      <label>
        <span class="text-gray-600">Target id</span>
        <input v-model="filters.target_id" type="number" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <label>
        <span class="text-gray-600">From</span>
        <input v-model="filters.date_from" type="datetime-local" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <label>
        <span class="text-gray-600">To</span>
        <input v-model="filters.date_to" type="datetime-local" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <label>
        <span class="text-gray-600">Limit</span>
        <input v-model="filters.limit" type="number" min="1" max="200" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <label>
        <span class="text-gray-600">Offset</span>
        <input v-model="filters.offset" type="number" min="0" class="mt-1 w-full border rounded-md px-2 py-1.5" />
      </label>
      <div class="col-span-2 md:col-span-4">
        <button type="submit" class="px-4 py-2 rounded-md bg-gray-900 text-white text-sm" :disabled="loading">
          {{ loading ? 'Loading…' : 'Apply filters' }}
        </button>
      </div>
    </form>

    <div class="overflow-x-auto border border-gray-200 rounded-lg">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">Id</th>
            <th class="px-3 py-2">When</th>
            <th class="px-3 py-2">Actor</th>
            <th class="px-3 py-2">Action</th>
            <th class="px-3 py-2">Target</th>
            <th class="px-3 py-2">Meta</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id" class="border-t border-gray-100 align-top">
            <td class="px-3 py-2 tabular-nums">{{ row.id }}</td>
            <td class="px-3 py-2 whitespace-nowrap">{{ row.created_at }}</td>
            <td class="px-3 py-2">{{ row.actor_user_id }}</td>
            <td class="px-3 py-2">{{ row.action }}</td>
            <td class="px-3 py-2">{{ row.target_type }} #{{ row.target_id }}</td>
            <td class="px-3 py-2 font-mono text-xs max-w-xs truncate">{{ JSON.stringify(row.metadata || row.meta || {}) }}</td>
          </tr>
          <tr v-if="!loading && !rows.length">
            <td colspan="6" class="px-3 py-6 text-center text-gray-500">No audit rows</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
