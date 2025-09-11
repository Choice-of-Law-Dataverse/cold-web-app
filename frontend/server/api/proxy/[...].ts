import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const origin = getHeader(event, 'origin')
  const referer = getHeader(event, 'referer')
  const host = getHeader(event, 'host')

  const allowedOrigins = [
    `http://localhost:3000`,
    `https://${host}`,
    `http://${host}`,
  ]

  const isValidOrigin =
    !origin ||
    allowedOrigins.some(
      (allowed) =>
        origin === allowed || (referer && referer.startsWith(allowed))
    )

  if (!isValidOrigin) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Forbidden: Invalid origin',
    })
  }

  const path = event.path.replace(/^\/api\/proxy\//, '')

  const url = joinURL(config.apiBaseUrl, path)

  return proxyRequest(event, url, {
    headers: {
      Authorization: `Bearer ${config.fastApiToken}`,
    },
  })
})
