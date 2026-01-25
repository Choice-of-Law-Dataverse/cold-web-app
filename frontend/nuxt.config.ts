import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  future: {
    compatibilityVersion: 4,
  },
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
  routeRules: {
    // Prerender static pages
    "/about/**": { prerender: true },
    "/learn/**": { prerender: true },
    "/disclaimer": { prerender: true },
    "/contact": { prerender: true },
    "/submit": { prerender: true },
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
    typeCheck: false,
  },
  vite: {
    plugins: [tailwindcss()],
    // Suppress OpenTelemetry 'this' keyword warnings (ESM compatibility)
    optimizeDeps: {
      exclude: ["@opentelemetry/api"],
    },
    build: {
      rollupOptions: {
        onwarn(warning, warn) {
          if (
            warning.code === "THIS_IS_UNDEFINED" &&
            warning.id?.includes("@opentelemetry")
          ) {
            return;
          }
          warn(warning);
        },
      },
    },
  },
  modules: [
    "@nuxt/ui",
    "@nuxt/fonts",
    "@nuxtjs/leaflet",
    "@nuxt/icon",
    "@nuxt/content",
    "@nuxtjs/robots",
    "@nuxtjs/sitemap",
    "@nuxt/scripts",
    "@nuxt/eslint",
    "@auth0/auth0-nuxt",
  ],
  runtimeConfig: {
    apiBaseUrl: process.env.NUXT_API_BASE_URL,
    apiKey: process.env.NUXT_API_KEY,
    logfire: {
      token: process.env.NUXT_LOGFIRE_TOKEN,
      serviceName: "frontend",
      serviceVersion: "1.0.0",
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
  colorMode: {
    preference: "light",
  },
  css: ["@/assets/styles.css"],
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
