import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useApiClient } from '~/composables/useApiClient'

const fetchUserInfo = async () => {
  const { apiClient } = useApiClient()

  try {
    // Initial request to get the client hints
    await apiClient('/get_user_info', {
      method: 'GET',
    })

    // After getting client hints from the browser, make a second request
    return await apiClient('/user_info', {
      method: 'GET',
    })
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null
  }
}

const getBrowserInfo = () => {
  if (typeof window === 'undefined') return {}
  const userAgent = navigator.userAgent
  const platform = navigator.platform
  const language = navigator.language
  const screenWidth = window.screen.width
  const screenHeight = window.screen.height

  return {
    userAgent,
    platform,
    language,
    screenWidth,
    screenHeight,
  }
}

const fetchSearchResults = async ({
  query,
  filters,
  page = 1,
  pageSize = 10,
}) => {
  const { apiClient } = useApiClient()

  const body = {
    search_string: query || '',
    page,
    page_size: pageSize,
    filters: [],
  }

  // Add sort_by_date if needed
  if (filters.sortBy === 'date') {
    body.sort_by_date = true
  } else {
    body.sort_by_date = false
  }

  // Add "Jurisdictions" filter if defined
  if (filters.jurisdiction) {
    body.filters.push({
      column: 'jurisdictions',
      values: filters.jurisdiction.split(','),
    })
  }

  // Add "Themes" filter if defined
  if (filters.theme) {
    body.filters.push({
      column: 'themes',
      values: filters.theme.split(','),
    })
  }

  // Set up mapping: Filter options have different wording to table names
  const typeFilterMapping = {
    Questions: 'Answers',
    'Court Decisions': 'Court Decisions',
    'Legal Instruments': 'Domestic Instruments',
    'Domestic Instruments': 'Domestic Instruments',
    'Regional Instruments': 'Regional Instruments',
    'International Instruments': 'International Instruments',
    Literature: 'Literature',
  }

  // Add "Type" filter if defined
  if (filters.type) {
    body.filters.push({
      column: 'tables',
      values: filters.type.split(',').map((type) => typeFilterMapping[type]),
    })
  }

  // Retrieve hostname safely (client only)
  const userHost =
    typeof window !== 'undefined' ? window.location.hostname : 'unknown'

  // Fetch user's IP address
  body.ip_address = 'Unknown'

  try {
    const data = await apiClient('https://api.ipify.org?format=json')

    body.ip_address = data.ip
  } catch (error) {
    console.warn('Could not fetch IP address:', error)
  }

  // Fetch detailed user info (browser, platform, etc.)
  const userInfo = await fetchUserInfo()
  const browserInfo = getBrowserInfo()

  // Add additional data to requestBody
  body.browser_info_navigator = browserInfo
  body.browser_info_hint = userInfo || {}
  body.hostname = userHost

  try {
    const data = await apiClient('/search/', { body })

    return {
      results: Object.values(data.results),
      totalMatches: data.total_matches || 0,
    }
  } catch (err) {
    throw new Error(`Search failed: ${err.message}`)
  }
}

export function useSearch(searchParams) {
  return useQuery({
    queryKey: ['search', searchParams],
    queryFn: () => fetchSearchResults(searchParams.value),
    enabled: computed(() => {
      // Enable query when we have search params
      const params = searchParams.value
      return !!(
        params.query ||
        params.filters.jurisdiction ||
        params.filters.theme ||
        params.filters.type
      )
    }),
    keepPreviousData: true, // Keep previous results while loading new ones
  })
}
