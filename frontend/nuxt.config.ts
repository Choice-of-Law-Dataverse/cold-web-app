// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@nuxtjs/tailwindcss', '@nuxt/fonts'],
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