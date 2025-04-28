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
  ],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL,
      apiBaseUrlPagination: process.env.API_BASE_URL_PAGINATION,
      FASTAPI: process.env.FASTAPI_API_TOKEN
    }
  },
  robots: {
    robotsTxt: true,
    sitemap: [
      '/sitemap.txt',
    ],
    groups: [
      {
        allow: ['/'],
        disallow: ['/search'],
      },
    ]
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
      anchorLinks: false,
    }
  },
  colorMode: {
    preference: 'light'
  },
  css: ['@/assets/styles.scss', 'tailwindcss/tailwind.css'], // Tailwind last
  tailwindcss: {
    configPath: './tailwind.config.js',
  },
  vite: {
    optimizeDeps: {
      include: ["plotly.js-dist-min"],
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
    presets: ['vue']
  },
});