// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@nuxtjs/tailwindcss'],
  css: ['@/assets/styles.scss', 'tailwindcss/tailwind.css'], // Tailwind last
  tailwindcss: {
    configPath: './tailwind.config.js',
  },
})
