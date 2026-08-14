<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { authUserStore } from '@/stores/authUserStore'

const toast = useToast()
const userStore = authUserStore()

const ROLES = ['admin', 'artist', 'employer', 'seller']

const targetUserId = ref('')
const selectedRole = ref('artist')
const lastResult = ref(null)
const busy = ref(false)

async function assignRole() {
  const uid = Number(targetUserId.value)
  if (!uid) {
    toast.error('Enter a valid user id')
    return
  }
  if (uid === userStore.authUserId) {
    toast.error('Cannot modify your own roles')
    return
  }
  busy.value = true
  try {
    const { data } = await axios.post(`/api/admin/users/${uid}/roles`, {
      role: selectedRole.value,
    })
    lastResult.value = data
    toast.success(`Assigned ${selectedRole.value}`)
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busy.value = false
  }
}

async function revokeRole() {
  const uid = Number(targetUserId.value)
  if (!uid) {
    toast.error('Enter a valid user id')
    return
  }
  if (uid === userStore.authUserId) {
    toast.error('Cannot modify your own roles')
    return
  }
  busy.value = true
  try {
    const { data } = await axios.delete(
      `/api/admin/users/${uid}/roles/${selectedRole.value}`
    )
    lastResult.value = data
    toast.success(`Revoked ${selectedRole.value}`)
  } catch (e) {
    toast.error(e?.response?.data?.detail || e.message)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="space-y-6 max-w-lg">
    <p class="text-sm text-gray-600">
      Assign or revoke roles by user id. You cannot change your own roles.
    </p>
    <label class="block text-sm">
      <span class="text-gray-700">User id</span>
      <input
        v-model="targetUserId"
        type="number"
        min="1"
        class="mt-1 w-full border border-gray-300 rounded-md px-3 py-2"
      />
    </label>
    <label class="block text-sm">
      <span class="text-gray-700">Role</span>
      <select
        v-model="selectedRole"
        class="mt-1 w-full border border-gray-300 rounded-md px-3 py-2"
      >
        <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
      </select>
    </label>
    <div class="flex gap-3">
      <button
        type="button"
        class="px-4 py-2 rounded-md bg-gray-900 text-white text-sm disabled:opacity-50"
        :disabled="busy"
        @click="assignRole"
      >
        Assign
      </button>
      <button
        type="button"
        class="px-4 py-2 rounded-md border border-gray-300 text-sm disabled:opacity-50"
        :disabled="busy"
        @click="revokeRole"
      >
        Revoke
      </button>
    </div>
    <pre
      v-if="lastResult"
      class="text-xs bg-gray-50 border border-gray-200 rounded-md p-3 overflow-auto"
    >{{ JSON.stringify(lastResult, null, 2) }}</pre>
  </div>
</template>
