import { computed } from 'vue'
import { useRecordDetails } from '@/composables/useRecordDetails'

export function useJurisdiction(iso3: Ref<string>) {
  const base = useRecordDetails(
    computed(() => 'Jurisdictions'),
    computed(() => iso3.value && iso3.value.toUpperCase())
  )

  const data = computed(() => {
    const rec = base.data.value
    if (!rec) return null
    return {
      ...rec,
      Name: rec?.Name || 'N/A',
      'Jurisdiction Summary': rec?.['Jurisdiction Summary'] || 'N/A',
      'Jurisdictional Differentiator':
        rec?.['Jurisdictional Differentiator'] || 'N/A',
      'Legal Family': rec?.['Legal Family'] || 'N/A',
      Specialists: rec?.Specialists || '',
      Literature: rec?.Literature,
    }
  })

  return { ...base, data }
}
