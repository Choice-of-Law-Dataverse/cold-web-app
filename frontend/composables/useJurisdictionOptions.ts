import { useFullTable } from '@/composables/useFullTable'

export function useJurisdictionOptions() {
  return useFullTable('Jurisdictions', {
    select: (data) =>
      data
        .filter((entry: any) => entry['Irrelevant?'] === false)
        .map((entry: any) => ({
          label: entry.Name as string,
          alpha3Code: entry['Alpha-3 Code'] as string | undefined,
          avatar: entry['Alpha-3 Code']
            ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${String(
                entry['Alpha-3 Code']
              ).toLowerCase()}.svg`
            : undefined,
        }))
        .sort((a: any, b: any) => (a.label || '').localeCompare(b.label || '')),
  })
}
