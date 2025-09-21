import { type Ref } from 'vue'
import { useFullTable } from '@/composables/useFullTable'

function convert(record: any) {
  return {
    ...record,
    Name: record?.Name || 'N/A',
    'Jurisdiction Summary': record?.['Jurisdiction Summary'] || 'N/A',
    'Jurisdictional Differentiator':
      record?.['Jurisdictional Differentiator'] || 'N/A',
    'Legal Family': record?.['Legal Family'] || 'N/A',
    Specialists: record?.Specialists || '',
    Literature: record?.Literature,
    label: record.Name as string,
    alpha3Code: record['Alpha-3 Code'] as string | undefined,
    avatar: record['Alpha-3 Code']
      ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${String(
          record['Alpha-3 Code']
        ).toLowerCase()}.svg`
      : undefined,
  }
}

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useJurisdictions(options: Options = {}) {
  return useFullTable('Jurisdictions', {
    ...options,
    select: (data) =>
      data
        .filter((record: any) => record['Irrelevant?'] === false)
        .map(convert)
        .sort((a: any, b: any) => (a.label || '').localeCompare(b.label || '')),
  })
}

export function useJurisdiction(iso3: Ref<string>, options: Options = {}) {
  return useFullTable('Jurisdictions', {
    ...options,
    select: (data) => {
      const record = data?.find(
        (r) => r?.['Alpha-3 Code'] === iso3.value.toLocaleUpperCase()
      )

      if (!record) return null

      return convert(record)
    },
  })
}
