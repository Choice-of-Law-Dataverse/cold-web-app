<template>
  <ul class="result-value-small section-gap list-none p-0 m-0">
    <!-- Domestic Legal Provision bullet point -->
    <template v-if="fallbackData && fallbackData['Domestic Legal Provisions']">
      <li
        v-for="(provision, index) in fallbackData[
          'Domestic Legal Provisions'
        ].split(',')"
        :key="'domestic-legal-' + index"
        class="section-gap p-0 m-0"
      >
        <LegalProvisionRenderer
          :value="provision"
          :fallbackData="fallbackData"
        />
      </li>
    </template>
    <template
      v-else-if="fallbackData && fallbackData['Domestic Instruments ID']"
    >
      <li
        v-for="(instrument, index) in fallbackData[
          'Domestic Instruments ID'
        ].split(',')"
        :key="'domestic-instrument-' + index"
        class="section-gap p-0 m-0"
      >
        <LegalProvisionRenderer
          skipArticle
          :value="instrument"
          :fallbackData="fallbackData"
        />
      </li>
    </template>
    <!-- Updated OUP Chapter bullet point -->
    <template v-if="fallbackData && fallbackData['Literature']">
      <template v-if="literatures?.length">
        <li
          v-for="(item, index) in literatures"
          :key="index"
          class="section-gap p-0 m-0"
        >
          <a :href="`/literature/${item.id}`">{{ item.title }}</a>
        </li>
      </template>
      <li v-else-if="literaturesLoading" class="section-gap p-0 m-0">
        <LoadingBar class="pt-[9px]" />
      </li>
    </template>
    <template v-else>
      <li v-if="isLoading" class="section-gap p-0 m-0">
        <LoadingBar class="pt-[9px]" />
      </li>
      <li v-else-if="oupChapterSource" class="section-gap p-0 m-0">
        <a :href="`/literature/${oupChapterSource.id}`">{{
          oupChapterSource.title
        }}</a>
      </li>
      <!-- If not loading and no OUP chapter, hide section (render nothing) -->
    </template>
  </ul>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LegalProvisionRenderer from '@/components/legal/LegalProvisionRenderer.vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
import { useLiteratures } from '@/composables/useLiteratures'

const props = defineProps({
  sources: {
    type: Array,
    required: true,
  },
  fallbackData: {
    type: Object,
    required: true,
  },
  valueClassMap: {
    type: Object,
    required: true,
  },
  valueClass: {
    type: String,
    default: 'result-value-small',
  },
  noLinkList: {
    type: Array,
    default: () => [],
  },
  fetchOupChapter: {
    type: Boolean,
    default: false,
  },
  fetchPrimarySource: {
    type: Boolean,
    default: false,
  },
})

const primarySource = ref([])
const oupChapterSource = ref(null)
const oupChapterLoading = ref(false)

const { data: literaturesByJurisdiction, isLoading } =
  useLiteratureByJurisdiction(
    computed(() => props.fallbackData['Jurisdictions'] || null)
  )

watch(
  () => literaturesByJurisdiction,
  (newVal) => {
    newVal.value?.forEach((item) => {
      if (item['OUP JD Chapter'] && props.fetchOupChapter) {
        oupChapterSource.value = { title: item.Title, id: item.ID }
      } else {
        primarySource.value.push({ title: item.Title, id: item.ID })
      }
    })
  },
  { immediate: true }
)

const { data: literatures, isLoading: literaturesLoading } = useLiteratures(
  computed(() => props.fallbackData['Jurisdictions'] || null)
)
</script>
