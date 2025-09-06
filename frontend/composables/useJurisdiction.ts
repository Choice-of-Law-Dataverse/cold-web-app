import { useFullTable } from '@/composables/useFullTable'

export function useJurisdiction(iso3: Ref<string>) {
  return useFullTable (
    'Jurisdictions',
    {
      select: (data) => 
        {
        const record = data?.find(r => r?.['Alpha-3 Code'] === iso3.value.toLocaleUpperCase())

        if(!record) return null

        return {
          ...record,
          Name: record?.Name || 'N/A',
          'Jurisdiction Summary': record?.['Jurisdiction Summary'] || 'N/A',
          'Jurisdictional Differentiator':
            record?.['Jurisdictional Differentiator'] || 'N/A',
          'Legal Family': record?.['Legal Family'] || 'N/A',
          Specialists: record?.Specialists || '',
          Literature: record?.Literature,
        }
      }
    }
  )
}
