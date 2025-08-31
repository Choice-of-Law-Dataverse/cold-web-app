import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

const fetchUserInfo = async () => {
  try {
    const config = useRuntimeConfig()
    // Initial request to get the client hints
    await fetch(`${config.public.apiBaseUrl}/get_user_info`, {
      method: 'GET',
    })

    // After getting client hints from the browser, make a second request
    const response = await fetch(`${config.public.apiBaseUrl}/user_info`, {
      method: 'GET',
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch user info: ${response.statusText}`)
    }

    const data = await response.json()
    return data
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
  const config = useRuntimeConfig()

  const requestBody = {
    search_string: query || '',
    page,
    page_size: pageSize,
    filters: [],
  }

  // Add sort_by_date if needed
  if (filters.sortBy === 'date') {
    requestBody.sort_by_date = true
  } else {
    requestBody.sort_by_date = false
  }

  // Add "Jurisdictions" filter if defined
  if (filters.jurisdiction) {
    requestBody.filters.push({
      column: 'jurisdictions',
      values: filters.jurisdiction.split(','),
    })
  }

  // Add "Themes" filter if defined
  if (filters.theme) {
    requestBody.filters.push({
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
    requestBody.filters.push({
      column: 'tables',
      values: filters.type.split(',').map((type) => typeFilterMapping[type]),
    })
  }

  // Retrieve hostname safely (client only)
  const userHost =
    typeof window !== 'undefined' ? window.location.hostname : 'unknown'

  // Fetch user's IP address
  let userIp = 'Unknown'
  try {
    const ipResponse = await fetch('https://api.ipify.org?format=json')
    const ipData = await ipResponse.json()
    if (ipData.ip) {
      userIp = ipData.ip
    }
  } catch (error) {
    console.warn('Could not fetch IP address:', error)
  }

  // Fetch detailed user info (browser, platform, etc.)
  const userInfo = await fetchUserInfo()
  const browserInfo = getBrowserInfo()

  // Add additional data to requestBody
  requestBody.ip_address = userIp
  requestBody.browser_info_navigator = browserInfo
  requestBody.browser_info_hint = userInfo || {}
  requestBody.hostname = userHost

  const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })

  if (!response.ok) {
    // Handle 5xx errors
    if (response.status >= 500) {
      throw new Error(
        `Server error (${response.status}): ${response.statusText}`
      )
    }
    // Handle other errors
    throw new Error(`API error (${response.status}): ${response.statusText}`)
  }

  const data = await response.json()

  return {
    results: Object.values(data.results),
    totalMatches: data.total_matches || 0,
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
