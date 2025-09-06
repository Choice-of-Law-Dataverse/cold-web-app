// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  ssr: true, // Ensure SSR is enabled
  modules: [
    '@nuxt/ui',
    '@nuxtjs/tailwindcss',
    '@nuxt/fonts',
    '@nuxtjs/leaflet',
    '@nuxt/icon',
    '@nuxt/content',
    'nuxt-purgecss',
    'nuxt-plotly',
    '@nuxtjs/robots',
    '@nuxtjs/sitemap',
    '@nuxt/scripts',
    '@nuxtjs/turnstile',
  ],
  turnstile: {
    siteKey: process.env.NUXT_TURNSTILE_SITE_KEY,
    addValidateEndpoint: true, // adds server-side validate endpoint
  },
  runtimeConfig: {
    turnstile: {
      secretKey: process.env.NUXT_TURNSTILE_SECRET_KEY,
    },
    public: {
      apiBaseUrl: process.env.API_BASE_URL,
      FASTAPI: process.env.FASTAPI_API_TOKEN,
    },
  },
  robots: {
    robotsTxt: true,
    sitemap: ['/sitemap.txt'],
    groups: [
      {
        // Alpha: Allow nothing, disallow everything
        allow: [],
        disallow: ['/'],

        // Beta and Live: Disallow search, new and edit. Allow everything else
        // allow: ['/'],
        // disallow: ['/search', '*/new', '*/edit'],
      },
    ],
  },
  purgecss: {
    enabled: false, // Disable for the time being
    rejected: true, // Enable logging of rejected (removed) selectors
    content: [
      // Add paths
    ],
    safelist: [
      // Add styles to keep
    ],
  },
  content: {
    documentDriven: false,
    markdown: {
      anchorLinks: true,
    },
  },
  colorMode: {
    preference: 'light',
  },
  css: ['@/assets/styles.scss', 'tailwindcss/tailwind.css'], // Tailwind last
  tailwindcss: {
    configPath: './tailwind.config.js',
  },
  vite: {
    optimizeDeps: {
      include: ['plotly.js-dist-min'],
    },
    // Fix legacy JS bug (https://stackoverflow.com/a/79054778/22393957)
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern',
        },
      },
    },
  },
  app: {
    head: {
      title: 'CoLD',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
  imports: {
    dirs: ['utils'],
    presets: ['vue'],
  },
})
