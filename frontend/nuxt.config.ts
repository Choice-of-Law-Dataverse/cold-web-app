export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: true,
  nitro: {
    prerender: {
      crawlLinks: true,
    },
    experimental: {
      tasks: false,
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
    "@nuxt/eslint",
    "@auth0/auth0-nuxt",
  ],
  runtimeConfig: {
    apiBaseUrl: process.env.NUXT_API_BASE_URL,
    apiKey: process.env.NUXT_API_KEY,
    azureStorageAccountName: process.env.AZURE_STORAGE_ACCOUNT_NAME,
    azureStorageConnectionString: process.env.AZURE_STORAGE_CONNECTION_STRING,
    azureTempContainerName:
      process.env.AZURE_TEMP_CONTAINER_NAME || "temp-uploads",
    logfire: {
      token: process.env.NUXT_LOGFIRE_TOKEN,
      serviceName: process.env.LOGFIRE_SERVICE_NAME || "cold-frontend-server",
      serviceVersion: process.env.LOGFIRE_SERVICE_VERSION || "1.0.0",
    },
    r2: {
      accountId: process.env.NUXT_R2_ACCOUNT_ID,
      bucketName: process.env.NUXT_R2_BUCKET_NAME,
      accessKeyId: process.env.NUXT_R2_ACCESS_KEY_ID,
      secretAccessKey: process.env.NUXT_R2_SECRET_ACCESS_KEY,
    },
    auth0: {
      appBaseUrl: process.env.NUXT_SITE_URL,
      audience: process.env.AUTH0_AUDIENCE,
      clientId: process.env.AUTH0_CLIENT_ID,
      clientSecret: process.env.AUTH0_CLIENT_SECRET,
      domain: "login.cold.global",
      sessionSecret: process.env.AUTH0_SECRET,
    },
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
    dirs: [],
    presets: ["vue"],
  },
});
