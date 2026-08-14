<script setup>
import { RouterView } from 'vue-router'
import AdminNav from '@/components/Admin/AdminNav.vue'
</script>

<template>
  <div class="min-h-screen pl-24 pr-8 py-8 max-w-5xl">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold text-gray-900">Admin</h1>
      <p class="text-sm text-gray-500 mt-1">Core ops — roles, audit, content moderation</p>
    </header>
    <AdminNav />
    <RouterView />
  </div>
</template>
