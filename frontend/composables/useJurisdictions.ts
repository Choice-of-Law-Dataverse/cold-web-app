import { useFullTable } from '@/composables/useFullTable'

export function useJurisdictions() {
  return useFullTable('Jurisdictions', {
    select: (data) => {
      // Filter jurisdictions (only relevant ones)
      const relevantJurisdictions = data.filter(
        (entry: any) => entry['Irrelevant?'] === false
      )

      // Extract "Name" field
      const jurisdictionNames: string[] = relevantJurisdictions
        .map((entry: any) => entry.Name)
        .filter(
          (name: any): name is string =>
            Boolean(name) && typeof name === 'string'
        )

      // Sort alphabetically
      const uniqueNames = [...new Set(jurisdictionNames)]
      return uniqueNames.sort((a, b) => a.localeCompare(b))
    },
  })
}
