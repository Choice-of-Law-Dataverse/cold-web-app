<template>
  <!-- Use the shared detail layout to match spacing, container width, and card styling. -->
  <!-- Use sourceTable="Loading" so the header stays hidden, yielding a clean blank card. -->
  <BaseDetailLayout
    :loading="loading"
    :resultData="resultData"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Arbitral Award"
  >
    <template #full-width>
      <div class="px-6 py-6">
        <h1 class="mb-6">Arbitral Awards</h1>
        <UTable :columns="columns" :rows="people" />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'

useHead({
  title: 'Arbitral Awards — CoLD',
})

// Minimal props for BaseDetailLayout to render a blank card with the same layout
const loading = false
const resultData = {} as any
const computedKeyLabelPairs: any[] = []
const valueClassMap: Record<string, string> = {}

// Demo table data (from Nuxt UI docs)
const columns = [
  {
    key: 'id',
    label: 'ID',
  },
  {
    key: 'name',
    label: 'Name',
    sortable: true,
  },
  {
    key: 'title',
    label: 'Title',
    sortable: true,
  },
  {
    key: 'email',
    label: 'Email',
    sortable: true,
    direction: 'desc' as const,
  },
  {
    key: 'role',
    label: 'Role',
  },
]

const people = [
  {
    id: 1,
    name: 'Lindsay Walton',
    title: 'Front-end Developer',
    email: 'lindsay.walton@example.com',
    role: 'Member',
  },
  {
    id: 2,
    name: 'Courtney Henry',
    title: 'Designer',
    email: 'courtney.henry@example.com',
    role: 'Admin',
  },
  {
    id: 3,
    name: 'Tom Cook',
    title: 'Director of Product',
    email: 'tom.cook@example.com',
    role: 'Member',
  },
  {
    id: 4,
    name: 'Whitney Francis',
    title: 'Copywriter',
    email: 'whitney.francis@example.com',
    role: 'Admin',
  },
  {
    id: 5,
    name: 'Leonard Krasner',
    title: 'Senior Designer',
    email: 'leonard.krasner@example.com',
    role: 'Owner',
  },
  {
    id: 6,
    name: 'Floyd Miles',
    title: 'Principal Designer',
    email: 'floyd.miles@example.com',
    role: 'Member',
  },
]
</script>
