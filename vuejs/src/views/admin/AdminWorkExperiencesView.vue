<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

const rows = ref([])
const loading = ref(false)
const statusFilter = ref('pending')
const busyId = ref(null)

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/job-market/admin/work-experiences', {
      params: { status: statusFilter.value, limit: 100 },
    })
    rows.value = data
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

async function decide(row, action) {
  if (!row.company_id) {
    toast.error('No company linked — cannot decide')
    return
  }
  busyId.value = row.id
  try {
    await axios.post(`/api/job-market/admin/work-experiences/${row.id}/${action}`)
    toast.success(action === 'approve' ? 'Approved' : 'Rejected')
    await load()
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <label class="text-sm">
        Status
        <select v-model="statusFilter" class="ml-2 border rounded-md px-2 py-1" @change="load">
          <option value="pending">pending</option>
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
        </select>
      </label>
      <button type="button" class="text-sm underline" @click="load">Refresh</button>
    </div>

    <div class="border border-gray-200 rounded-lg overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">Id</th>
            <th class="px-3 py-2">Artist</th>
            <th class="px-3 py-2">Company</th>
            <th class="px-3 py-2">Title</th>
            <th class="px-3 py-2">Type</th>
            <th class="px-3 py-2">Dates</th>
            <th class="px-3 py-2">Status</th>
            <th class="px-3 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id" class="border-t border-gray-100 align-top">
            <td class="px-3 py-2 tabular-nums">{{ row.id }}</td>
            <td class="px-3 py-2">
              {{ row.artist_username || '—' }}
              <div class="text-gray-500">#{{ row.artist_user_id || row.user_id }}</div>
            </td>
            <td class="px-3 py-2">
              {{ row.company_name }}
              <div class="text-gray-500">co #{{ row.company_id ?? '—' }}</div>
            </td>
            <td class="px-3 py-2">{{ row.title }}</td>
            <td class="px-3 py-2">{{ row.employment_type }}</td>
            <td class="px-3 py-2 whitespace-nowrap">
              {{ row.start_date }} → {{ row.end_date || 'present' }}
            </td>
            <td class="px-3 py-2">{{ row.status }}</td>
            <td class="px-3 py-2">
              <div v-if="row.status === 'pending'" class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="px-2 py-1 rounded bg-gray-900 text-white text-xs disabled:opacity-50"
                  :disabled="busyId === row.id || !row.company_id"
                  @click="decide(row, 'approve')"
                >
                  Approve
                </button>
                <button
                  type="button"
                  class="px-2 py-1 rounded border text-xs disabled:opacity-50"
                  :disabled="busyId === row.id || !row.company_id"
                  @click="decide(row, 'reject')"
                >
                  Reject
                </button>
              </div>
              <span v-else class="text-gray-400">—</span>
            </td>
          </tr>
          <tr v-if="!loading && !rows.length">
            <td colspan="8" class="px-3 py-6 text-center text-gray-500">No work experiences</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
