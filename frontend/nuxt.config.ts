import { resolve } from "node:path";

const projectRoot = process.cwd();

export default defineNuxtConfig({
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: true,
  srcDir: "app",
  alias: {
    "@": resolve(projectRoot, "app"),
  },
  nitro: {
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
    typeCheck: false,
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
    "@nuxtjs/turnstile",
    "@nuxt/eslint",
  ],
  turnstile: {
    siteKey: process.env.NUXT_TURNSTILE_SITE_KEY,
    addValidateEndpoint: true,
  },
  site: {
    url: process.env.NUXT_SITE_URL || "https://cold.global",
  },
  runtimeConfig: {
    turnstile: {
      secretKey: process.env.NUXT_TURNSTILE_SECRET_KEY,
    },
    apiBaseUrl: process.env.API_BASE_URL,
    fastApiToken: process.env.FASTAPI_API_TOKEN,
    public: {
      siteUrl: process.env.NUXT_SITE_URL || "https://cold.global",
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
  content: {
    renderer: {
      anchorLinks: true,
    },
  },
  colorMode: {
    preference: "light",
  },
  css: ["@/assets/styles.scss"],
  postcss: {
    plugins: {
      "@tailwindcss/postcss": {},
    },
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
