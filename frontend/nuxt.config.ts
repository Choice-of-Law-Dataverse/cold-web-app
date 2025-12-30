export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: true,
  nitro: {
    experimental: {
      tasks: false,
    },
    externals: {
      inline: ["@aws-sdk/client-s3", "@aws-sdk/s3-request-presigner"],
    },
  },
  $production: {
    scripts: {
      registry: {
        plausibleAnalytics: {
          domain: "cold.global",
        },
      },
    },
  },
  typescript: {
    typeCheck: true,
  },
  modules: [
    "@nuxt/ui",
    "@nuxtjs/tailwindcss",
    "@nuxt/fonts",
    "@nuxtjs/leaflet",
    "@nuxt/icon",
    "@nuxt/content",
    "nuxt-purgecss",
    "@nuxtjs/robots",
    "@nuxtjs/sitemap",
    "@nuxt/scripts",
    "@nuxtjs/turnstile",
    "@nuxt/eslint",
  ],
  turnstile: {
    siteKey: process.env.NUXT_TURNSTILE_SITE_KEY,
    addValidateEndpoint: true,
  },
  runtimeConfig: {
    turnstile: {
      secretKey: process.env.NUXT_TURNSTILE_SECRET_KEY,
    },
    apiBaseUrl: process.env.API_BASE_URL,
    fastApiToken: process.env.FASTAPI_API_TOKEN,
    r2AccountId: process.env.R2_ACCOUNT_ID,
    r2BucketName: process.env.R2_BUCKET_NAME,
    r2AccessKeyId: process.env.R2_ACCESS_KEY_ID,
    r2SecretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
    public: {
      siteUrl: process.env.NUXT_SITE_URL,
    },
  },
  robots: {
    robotsTxt: true,
    sitemap: ["/sitemap.txt"],
    groups: [
      {
        allow: [],
        disallow: ["/"],
      },
    ],
  },
  purgecss: {
    enabled: false,
    rejected: true,
    content: [],
    safelist: [],
  },
  content: {
    documentDriven: false,
    markdown: {
      anchorLinks: true,
    },
  },
  colorMode: {
    preference: "light",
  },
  css: ["@/assets/styles.scss", "tailwindcss/tailwind.css"],
  tailwindcss: {
    configPath: "./tailwind.config.js",
  },
  app: {
    head: {
      title: "CoLD",
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1" },
      ],
    },
  },
  imports: {
    dirs: ["utils"],
    presets: ["vue"],
  },
});
