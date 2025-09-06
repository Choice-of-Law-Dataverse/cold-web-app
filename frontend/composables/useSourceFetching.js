import { ref } from 'vue'

export function useSourceFetching({
  jurisdiction,
  fetchOupChapter = false,
  fetchPrimarySource = false,
}) {
  const config = useRuntimeConfig()
  const primarySource = ref(null)
  const oupChapterSource = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchPrimarySourceData() {
    if (!jurisdiction) return

    const jsonPayload = {
      table: 'Literature',
      filters: [
        {
          column: 'Jurisdiction',
          value: jurisdiction,
        },
      ],
    }

    try {
      loading.value = true
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
      if (!response.ok) throw new Error('Failed to fetch primary source')

      const data = await response.json()

      // Filter out entries where "OUP JD Chapter" is explicitly true
      const nonOupEntries = data.filter(
        (entry) => entry['OUP JD Chapter'] === null
      )

      // Select the first valid non-OUP entry as the primary source
      if (nonOupEntries.length > 0) {
        primarySource.value = nonOupEntries.map((entry) => ({
          title: entry.Title,
          id: entry.ID,
        }))
      }
    } catch (err) {
      console.error('Error fetching primary source:', err)
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch primary source'
    } finally {
      loading.value = false
    }
  }

  async function fetchOupChapterSourceData() {
    if (!jurisdiction || !fetchOupChapter) return

    const jsonPayload = {
      table: 'Literature',
      filters: [
        {
          column: 'Jurisdiction',
          value: jurisdiction,
        },
        {
          column: 'OUP JD Chapter',
          value: true,
        },
      ],
    }

    try {
      loading.value = true
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

      if (!response.ok) throw new Error('Failed to fetch OUP JD Chapter source')

      const data = await response.json()
      if (data.length > 0) {
        oupChapterSource.value = { title: data[0].Title, id: data[0].ID }
      }
    } catch (err) {
      console.error('Error fetching OUP JD Chapter source:', err)
      error.value =
        err instanceof Error
          ? err.message
          : 'Failed to fetch OUP JD Chapter source'
    } finally {
      loading.value = false
    }
  }

  async function fetchAllSources() {
    if (fetchOupChapter) await fetchOupChapterSourceData()
    if (fetchPrimarySource) await fetchPrimarySourceData()
  }

  return {
    primarySource,
    oupChapterSource,
    loading,
    error,
    fetchAllSources,
  }
}
