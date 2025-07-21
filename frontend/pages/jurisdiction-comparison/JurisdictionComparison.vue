<template>
  <div>
    <!-- Main content in BaseDetailLayout -->
    <BaseDetailLayout
      :loading="false"
      :resultData="{}"
      :keyLabelPairs="[]"
      :valueClassMap="{}"
      sourceTable=""
    >
      <template #full-width>
        <!-- Create a container that ensures proper sticky behavior -->
        <div class="relative min-h-screen">
          <div class="px-6 py-4 md:pt-8">
            <!-- Sticky filters positioned within BaseDetailLayout -->
            <JCStickyFilters />

            <!-- Content area with sufficient height for sticky behavior -->
            <div class="md:mt-0 relative">
              <JCOverview />
              <JCMainQuestions :showCaret="false" />
              <JCMainQuestions />
              <JCMainQuestions />
            </div>
          </div>
        </div>
      </template>
    </BaseDetailLayout>
  </div>
</template>

<script setup>
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import JCOverview from '@/pages/jurisdiction-comparison/JCOverview.vue'
import JCMainQuestions from '@/pages/jurisdiction-comparison/JCMainQuestions.vue'
import JCStickyFilters from '@/pages/jurisdiction-comparison/JCStickyFilters.vue'
</script>
