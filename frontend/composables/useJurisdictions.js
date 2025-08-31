import { useQuery } from '@tanstack/vue-query'

const fetchJurisdictionsData = async () => {
  const config = useRuntimeConfig()
  const jsonPayload = { table: 'Jurisdictions', filters: [] }

  const response = await fetch(
    `${config.public.apiBaseUrl}/search/full_table`,
    {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    }
  )

  if (!response.ok) {
    throw new Error('Failed to load jurisdictions data')
  }

  const data = await response.json()

  // Filter jurisdictions (only relevant ones)
  const relevantJurisdictions = data.filter(
    (entry) => entry['Irrelevant?'] === false
  )

  // Extract "Name" field
  const jurisdictionNames = relevantJurisdictions
    .map((entry) => entry.Name)
    .filter(Boolean)

  // Sort alphabetically
  return [...new Set(jurisdictionNames)].sort((a, b) => a.localeCompare(b))
}

export function useJurisdictions() {
  return useQuery({
    queryKey: ['jurisdictions'],
    queryFn: fetchJurisdictionsData,
  })
}
