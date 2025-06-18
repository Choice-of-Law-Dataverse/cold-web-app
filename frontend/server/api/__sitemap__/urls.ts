import { defineSitemapEventHandler, useRuntimeConfig } from '#imports'

export default defineSitemapEventHandler(async () => {
  const config = useRuntimeConfig()
  const data = await $fetch(`${config.public.apiBaseUrl}/sitemap/urls`, {
    headers: {
      Authorization: `Bearer ${config.public.FASTAPI}`
    }
  })

  // Debug: log the raw API response
  console.log('Sitemap API response:', data)

  // Collect all URLs from all environments
  const urls: string[] = []
  for (const env of Object.values(data)) {
    if (env && Array.isArray(env.urls)) {
      urls.push(...env.urls)
    }
  }

  // Debug: log the collected URLs
  console.log('Collected URLs:', urls)

  // Map to sitemap format
  const sitemapUrls = urls.map(url => ({
    loc: url.replace(/^https?:\/\/[^/]+/, ''), // Convert absolute to relative path
  }))

  return sitemapUrls
})