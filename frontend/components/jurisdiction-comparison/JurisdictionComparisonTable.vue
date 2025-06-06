<template>
  <!-- Comparison Table -->
  <UTable
    v-if="!loading"
    class="styled-table"
    :rows="rows"
    :columns="columns"
    :ui="{
      th: {
        base: 'text-left rtl:text-right',
        padding: 'px-8 py-3.5',
        color: 'text-gray-900 dark:text-white',
        font: 'font-semibold',
        size: 'text-sm',
      },
      td: {
        padding: 'px-8 py-2',
      },
    }"
  >
    <!-- Custom Column Templates -->
    <template #Answer-data="{ row }">
      <NuxtLink :to="`/question/${row.ID}`">
        {{ row.Answer }}
      </NuxtLink>
    </template>

    <template #Match-data="{ row }">
      <span
        v-if="
          computeMatchStatus(row.Match.answer1, row.Match.answer2) !== 'red-x'
        "
        :style="{
          backgroundColor: getBackgroundColor(
            computeMatchStatus(row.Match.answer1, row.Match.answer2)
          ),
        }"
        class="inline-block w-4 h-4 rounded-full"
      ></span>
      <span
        v-else
        :style="{ color: 'var(--color-label-court-decision)' }"
        class="text-lg"
      >
        ✖
      </span>
    </template>

    <!-- Dynamic Columns -->
    <template
      v-for="column in columns"
      :key="column.key"
      #[`${column.key}-data`]="{ row }"
    >
      <!-- Handle dynamic 'Answer' columns -->
      <NuxtLink
        v-if="column.key.startsWith('Answer')"
        :to="`/question/${row[column.key + '_ID'] || row.ID}`"
      >
        <template
          v-if="
            typeof row[column.key] === 'string' && row[column.key].includes(',')
          "
        >
          <ul>
            <li v-for="(item, idx) in row[column.key].split(',')" :key="idx">
              {{ item.trim() }}
            </li>
          </ul>
        </template>
        <template v-else>
          {{ row[column.key] }}
        </template>
      </NuxtLink>

      <!-- Handle 'Match' column -->
      <template v-else-if="column.key === 'Match'">
        <template v-if="row.Match">
          <span
            v-if="
              computeMatchStatus(row.Match.answer1, row.Match.answer2) !==
              'red-x'
            "
            :style="{
              backgroundColor: getBackgroundColor(
                computeMatchStatus(row.Match.answer1, row.Match.answer2)
              ),
            }"
            class="inline-block w-4 h-4 rounded-full"
          ></span>
          <span
            v-else
            :style="{ color: 'var(--color-label-court-decision)' }"
            class="text-lg"
          >
            ✖
          </span>
        </template>
        <span v-else>Invalid Data</span>
      </template>

      <!-- Fallback for other columns -->
      <span v-else>
        {{ row[column.key] }}
      </span>
    </template>
  </UTable>
  <p v-else>Loading...</p>
</template>

<script setup>
const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  computeMatchStatus: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['update-rows'])

// Example function to update rows (emit changes back to parent)
function filterRows(newFilteredRows) {
  emit('update-rows', newFilteredRows)
}

function getBackgroundColor(status) {
  switch (status) {
    case 'green':
      return 'var(--color-cold-green)'
    case 'red':
      return 'var(--color-label-court-decision)'
    case 'gray':
      return 'var(--color-cold-gray)'
    default:
      return 'transparent'
  }
}
</script>

<style scoped>
.match-column {
  text-align: center;
}

.rounded-full {
  border-radius: 50%;
}

.inline-block {
  display: inline-block;
}

.w-4 {
  width: 12px;
}

.h-4 {
  height: 12px;
}
</style>
