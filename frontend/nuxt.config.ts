// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  ssr: true, // Ensure SSR is enabled
  modules: ['@nuxt/ui', '@nuxtjs/tailwindcss', '@nuxt/fonts', '@nuxtjs/leaflet', '@nuxt/icon', '@nuxt/content'],
  content: {
    documentDriven: true,
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
  // Fix legacy JS bug (https://stackoverflow.com/a/79054778/22393957)
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern',
        },
      },
    },
  },
});