import { defineSitemapEventHandler, useRuntimeConfig } from '#imports'

export default defineSitemapEventHandler(async () => {
  const config = useRuntimeConfig()
  const data = await $fetch(`${config.public.apiBaseUrl}/sitemap/urls`, {
    headers: {
      Authorization: `Bearer ${config.public.FASTAPI}`
    }
  })

  // Only use the 'beta' environment URLs
  const betaUrls: string[] = (data.beta && Array.isArray(data.beta.urls)) ? data.beta.urls : []

  // Map to sitemap format (relative paths)
  const sitemapUrls = betaUrls.map(url => ({
    loc: url.replace(/^https?:\/\/[^/]+/, ''),
  }))

  return sitemapUrls
})