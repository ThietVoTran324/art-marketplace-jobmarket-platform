<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

const targetUserId = ref('')
const rows = ref([])
const busy = ref(false)
const editingId = ref(null)
const form = ref({
  kind: 'education',
  title: '',
  organization: '',
  occurred_on: '',
  description: '',
})

function resetForm() {
  editingId.value = null
  form.value = {
    kind: 'education',
    title: '',
    organization: '',
    occurred_on: '',
    description: '',
  }
}

async function load() {
  const uid = Number(targetUserId.value)
  if (!uid) {
    toast.error('Enter user id')
    return
  }
  busy.value = true
  try {
    const { data } = await axios.get(`/api/job-market/users/${uid}/credentials`)
    rows.value = data
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busy.value = false
  }
}

function startEdit(row) {
  editingId.value = row.id
  form.value = {
    kind: row.kind,
    title: row.title || '',
    organization: row.organization || '',
    occurred_on: row.occurred_on || '',
    description: row.description || '',
  }
}

async function save() {
  const uid = Number(targetUserId.value)
  if (!uid) {
    toast.error('Enter user id')
    return
  }
  if (!form.value.title.trim()) {
    toast.error('Title required')
    return
  }
  const payload = {
    kind: form.value.kind,
    title: form.value.title.trim(),
    organization: form.value.organization.trim() || null,
    occurred_on: form.value.occurred_on || null,
    description: form.value.description.trim() || null,
  }
  busy.value = true
  try {
    if (editingId.value) {
      await axios.patch(
        `/api/job-market/admin/users/${uid}/credentials/${editingId.value}`,
        payload
      )
      toast.success('Updated')
    } else {
      await axios.post(`/api/job-market/admin/users/${uid}/credentials`, payload)
      toast.success('Created')
    }
    resetForm()
    await load()
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busy.value = false
  }
}

async function remove(row) {
  const uid = Number(targetUserId.value)
  if (!window.confirm(`Delete credential #${row.id}?`)) return
  busy.value = true
  try {
    await axios.delete(`/api/job-market/admin/users/${uid}/credentials/${row.id}`)
    toast.success('Deleted')
    if (editingId.value === row.id) resetForm()
    await load()
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="space-y-6 max-w-2xl">
    <div class="flex gap-2 items-end">
      <label class="flex-1 text-sm">
        <span class="text-gray-700">User id</span>
        <input
          v-model="targetUserId"
          type="number"
          min="1"
          class="mt-1 w-full border rounded-md px-3 py-2"
        />
      </label>
      <button
        type="button"
        class="px-4 py-2 rounded-md bg-gray-900 text-white text-sm disabled:opacity-50"
        :disabled="busy"
        @click="load"
      >
        Load
      </button>
    </div>

    <div class="border border-gray-200 rounded-lg overflow-hidden">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">Id</th>
            <th class="px-3 py-2">Kind</th>
            <th class="px-3 py-2">Title</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id" class="border-t border-gray-100">
            <td class="px-3 py-2">{{ row.id }}</td>
            <td class="px-3 py-2">{{ row.kind }}</td>
            <td class="px-3 py-2">{{ row.title }}</td>
            <td class="px-3 py-2 text-right space-x-2">
              <button type="button" class="underline" @click="startEdit(row)">Edit</button>
              <button type="button" class="underline text-red-700" @click="remove(row)">Delete</button>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="4" class="px-3 py-4 text-center text-gray-500">No credentials loaded</td>
          </tr>
        </tbody>
      </table>
    </div>

    <form class="space-y-3 border border-gray-200 rounded-lg p-4" @submit.prevent="save">
      <h2 class="font-medium">{{ editingId ? `Edit #${editingId}` : 'Create credential' }}</h2>
      <label class="block text-sm">
        Kind
        <select v-model="form.kind" class="mt-1 w-full border rounded-md px-3 py-2">
          <option value="education">education</option>
          <option value="licensing">licensing</option>
          <option value="award">award</option>
        </select>
      </label>
      <label class="block text-sm">
        Title
        <input v-model="form.title" class="mt-1 w-full border rounded-md px-3 py-2" required />
      </label>
      <label class="block text-sm">
        Organization
        <input v-model="form.organization" class="mt-1 w-full border rounded-md px-3 py-2" />
      </label>
      <label class="block text-sm">
        Occurred on
        <input v-model="form.occurred_on" type="date" class="mt-1 w-full border rounded-md px-3 py-2" />
      </label>
      <label class="block text-sm">
        Description
        <textarea v-model="form.description" rows="2" class="mt-1 w-full border rounded-md px-3 py-2" />
      </label>
      <div class="flex gap-2">
        <button type="submit" class="px-4 py-2 rounded-md bg-gray-900 text-white text-sm" :disabled="busy">
          Save
        </button>
        <button type="button" class="px-4 py-2 rounded-md border text-sm" @click="resetForm">
          Reset
        </button>
      </div>
    </form>
  </div>
</template>
