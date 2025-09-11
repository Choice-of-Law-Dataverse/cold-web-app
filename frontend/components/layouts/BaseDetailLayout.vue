<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="resultData"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          :formattedSourceTable="sourceTable"
          :formattedJurisdiction="formattedJurisdiction"
          :showHeader="showHeader"
          :showOpenLink="showOpenLink"
          :showSuggestEdit="showSuggestEdit"
          :formattedTheme="formattedTheme"
          :hideBackButton="hideBackButton"
          :headerMode="headerMode"
          :showNotificationBanner="showNotificationBanner"
          :notificationBannerMessage="notificationBannerMessage"
          :fallbackMessage="fallbackMessage"
          :icon="icon"
          @save="$emit('save')"
          @open-save-modal="$emit('open-save-modal')"
          @open-cancel-modal="$emit('open-cancel-modal')"
        >
          <slot />
          <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
            <slot :name="name" v-bind="slotData" />
          </template>
        </DetailDisplay>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import DetailDisplay from '@/components/ui/BaseDetailDisplay.vue'

const props = withDefaults(
  defineProps<{
    loading: boolean
    resultData: any
    keyLabelPairs: any[]
    valueClassMap: Record<string, string>
    sourceTable: string
    formattedJurisdiction?: any[] //
    hideBackButton?: boolean
    showHeader?: boolean
    formattedTheme?: any[]
    headerMode?: string
    showNotificationBanner?: boolean
    notificationBannerMessage?: string
    fallbackMessage?: string
    icon?: string
    showOpenLink?: boolean
    showSuggestEdit?: boolean
  }>(),
  {
    showHeader: true,
    showOpenLink: false,
    showSuggestEdit: false,
  }
)

defineEmits(['save', 'open-save-modal', 'open-cancel-modal'])
</script>
