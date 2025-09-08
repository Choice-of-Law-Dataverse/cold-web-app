import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const path = event.path.replace(/^\/api\/proxy\//, '')
  const url = joinURL(config.apiBaseUrl, path)

  return proxyRequest(event, url, {
    headers: {
      Authorization: `Bearer ${config.fastApiToken}`,
    },
  })
})
