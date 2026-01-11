import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const path = event.path.replace(/^\/api\/proxy\//, '')
  const url = joinURL(config.apiBaseUrl, path)

  const headers: Record<string, string> = {
    'X-API-Key': config.apiKey,
  }

  try {
    const result = await proxyRequest(event, url, { headers })

    return result
  } catch (error) {
    console.error('Proxy request error:', error)
    throw error
  }
})
