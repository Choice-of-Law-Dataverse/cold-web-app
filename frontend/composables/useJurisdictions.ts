import { useFullTable } from '@/composables/useFullTable'

function convert(record: Record<string, unknown>) {
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

export function useJurisdictions() {
  return useFullTable('Jurisdictions', {
    select: (data) =>
      data
        .filter(
          (record: Record<string, unknown>) => record['Irrelevant?'] === false
        )
        .map(convert)
        .sort((a: Record<string, unknown>, b: Record<string, unknown>) =>
          ((a.label as string) || '').localeCompare((b.label as string) || '')
        ),
  })
}

export function useJurisdiction(iso3: Ref<string>) {
  const result = useFullTable('Jurisdictions')

  const data = result.data?.value?.find(
    (r) => r?.['Alpha-3 Code'] === iso3.value.toLocaleUpperCase()
  )

  return {
    ...result,
    data: ref(convert(data || {})) as Ref<Record<string, unknown> | undefined>,
  }
}
