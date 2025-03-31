import { ref, computed, watch } from 'vue'

export function useJurisdiction() {
    const jurisdictionData = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const literatureTitle = ref(null)
    const specialists = ref([])
    const compareJurisdiction = ref(null)

    const config = useRuntimeConfig()

    const keyLabelPairs = [
        { key: 'Name', label: 'Name' },
        { key: 'Jurisdictional Differentiator', label: 'Jurisdictional Differentiator' },
        { key: 'Specialist', label: 'Specialists' },
        { key: 'Literature', label: 'Related Literature' }
    ]

    const valueClassMap = {
        Name: 'result-value-medium',
        'Jurisdictional Differentiator': 'result-value-small',
        Literature: 'result-value-small',
        'search-links': 'result-value-small',
    }

    async function fetchLiteratureTitle(ids) {
        if (!ids) {
            literatureTitle.value = ''
            return
        }

        // Split IDs if multiple are provided
        const idList = ids.split(',').map((id) => id.trim())

        try {
            const titles = await Promise.all(
                idList.map(async (id) => {
                    const jsonPayload = {
                        table: 'Literature',
                        id: id,
                    }
                    const response = await fetch(
                        `${config.public.apiBaseUrl}/search/details`,
                        {
                            method: 'POST',
                            headers: {
                                authorization: `Bearer ${config.public.FASTAPI}`,
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(jsonPayload),
                        }
                    )
                    if (!response.ok) throw new Error('Failed to fetch literature details')
                    const data = await response.json()
                    return data.Title || 'Unknown Title'
                })
            )
            literatureTitle.value = titles
        } catch (error) {
            console.error('Error fetching literature title:', error)
            literatureTitle.value = 'Error'
        }
    }

    async function fetchSpecialists(jurisdictionName) {
        if (!jurisdictionName) return

        try {
            const response = await fetch(
                `${config.public.apiBaseUrl}/search/full_table`,
                {
                    method: 'POST',
                    headers: {
                        authorization: `Bearer ${config.public.FASTAPI}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        table: 'Specialists',
                        filters: [{ column: 'Jurisdiction', value: jurisdictionName }],
                    }),
                }
            )

            if (!response.ok) throw new Error('Failed to fetch specialists')

            specialists.value = await response.json()
            // Update jurisdictionData with specialists
            if (jurisdictionData.value) {
                jurisdictionData.value.Specialists = specialists.value
            }
        } catch (error) {
            console.error('Error fetching specialists:', error)
            specialists.value = []
        }
    }

    async function fetchJurisdiction(iso3) {
        loading.value = true
        error.value = null

        const jsonPayload = {
            table: 'Jurisdictions',
            id: iso3.toUpperCase(),
        }

        try {
            const response = await fetch(
                `${config.public.apiBaseUrl}/search/details`,
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
                throw new Error(`Failed to fetch jurisdiction: ${response.statusText}`)
            }

            const data = await response.json()
            // Extract the required values
            jurisdictionData.value = {
                Name: data?.Name || 'N/A',
                'Jurisdictional Differentiator':
                    data?.['Jurisdictional Differentiator'] || 'N/A',
                Specialists: specialists.value // Include specialists in the data
            }

            // If "Literature" exists, fetch its title
            if (data?.Literature) {
                jurisdictionData.value.Literature = data.Literature
                await fetchLiteratureTitle(jurisdictionData.value.Literature)
            } else {
                literatureTitle.value = null
            }
        } catch (err) {
            error.value = err.message
            console.error('Error fetching jurisdiction:', err)
        } finally {
            loading.value = false
        }
    }

    // Watch for jurisdiction name changes to fetch specialists
    watch(
        () => jurisdictionData.value?.Name,
        (newName) => {
            if (newName) fetchSpecialists(newName)
        }
    )

    return {
        jurisdictionData,
        loading,
        error,
        literatureTitle,
        specialists,
        compareJurisdiction,
        keyLabelPairs,
        valueClassMap,
        fetchJurisdiction,
    }
} 