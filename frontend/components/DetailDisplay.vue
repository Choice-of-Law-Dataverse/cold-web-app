<template>
  <div class="container">
    <BackButton />
    <div class="col-span-12">
      <UCard>
        <!-- Header section -->
        <template #header>
          <div class="header-container">
            <!-- Left side of the header -->
            <div class="header-left">
              <!-- Display 'Name (from Jurisdiction)' or alternatives -->
              <span v-if="jurisdiction">{{ jurisdiction }}</span>

              <!-- Display 'formattedSourceTable' -->
              <span v-if="formattedSourceTable" class="source-table">
                {{ formattedSourceTable }}
              </span>

              <!-- Display 'Themes' -->
              <span v-if="formattedTheme" class="themes">
                {{ formattedTheme }}
              </span>
            </div>
          </div>
        </template>

        <!-- Main content -->
        <div class="detail-content">
          <div v-if="loading">Loading...</div>
          <div v-else>
            <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
            <div v-for="(item, index) in keyLabelPairs" :key="index">
              <p class="result-key">{{ item.label }}</p>
              <p class="result-value">{{ resultData?.[item.key] || 'N/A' }}</p>

              <!-- Insert hardcoded label after "Jurisdiction Names" -->
              <template v-if="item.key === 'Jurisdiction Names'">
                <p class="result-key">Label</p>
                <p class="result-value">{{ formattedSourceTable }}</p>
              </template>
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'
import BackButton from '~/components/BackButton.vue'

// Props for reusability across pages
const props = defineProps({
  loading: Boolean,
  resultData: Object,
  keyLabelPairs: Array,
  formattedSourceTable: {
    type: String,
    default: 'N/A',
  },
})

// Additional computed properties for other display elements
const jurisdiction = computed(
  () => props.resultData?.['Jurisdiction Names'] || null
)
const formattedTheme = computed(() => props.resultData?.Themes || null)
</script>
