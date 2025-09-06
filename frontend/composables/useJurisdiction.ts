import { computed } from 'vue'
import { useRecordDetails } from '@/composables/useRecordDetails'

export function useJurisdiction(iso3: Ref<string>) {
  return useRecordDetails(
    computed(() => 'Jurisdictions'),
    computed(() => iso3.value && iso3.value.toUpperCase()),
    {
      select: (data) => {
        return {
          ...data,
          Name: data?.Name || 'N/A',
          'Jurisdiction Summary': data?.['Jurisdiction Summary'] || 'N/A',
          'Jurisdictional Differentiator':
            data?.['Jurisdictional Differentiator'] || 'N/A',
          'Legal Family': data?.['Legal Family'] || 'N/A',
          Specialists: data?.Specialists || '',
          Literature: data?.Literature,
        }
      }
    }
  )
}
