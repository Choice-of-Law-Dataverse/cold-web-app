import tailwindcss from "@tailwindcss/vite";
import { AI_TRAINING_CRAWLERS } from "./config/aiTrainingCrawlers";
import { SITEMAP_GROUPS } from "./server/utils/sitemapSources";

const NON_PUBLIC_PATHS = ["/search", "/moderation", "*/new", "*/edit"];

/**
 * Routes kept out of every sitemap: gated pages, single-use flows and the
 * section stubs that only redirect.
 *
 * `/question/**` is not listed here — the `questions` source publishes the 60
 * comparative question pages. The ~15k jurisdiction-specific answers under the
 * same route are excluded by not being in that source, and carry `noindex`.
 */
const SITEMAP_EXCLUDE = [
  "/search",
  "/moderation/**",
  "/**/new",
  "/**/edit",
  "/confirmation",
  "/court-decision/my-analyses",
  "/event/**",
  "/about",
  "/learn",
];

const ENTITY_SITEMAPS = Object.fromEntries(
  Object.keys(SITEMAP_GROUPS).map((group) => [
    group,
    { sources: [`/api/__sitemap__/${group}`] },
  ]),
);

const CONTENT_SIGNAL = {
  search: "yes",
  "ai-input": "yes",
  "ai-train": "no",
} as const;

export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  future: {
    compatibilityVersion: 4,
  },
  devtools: { enabled: process.env.NODE_ENV === "development" },
  ssr: true,
  nitro: {
    compressPublicAssets: { brotli: true, gzip: true },
    prerender: {
      crawlLinks: false,
      routes: [],
    },
    experimental: {
      tasks: false,
    },
  },
  routeRules: {
    "/api/__sitemap__/**": {
      swr: 3600,
    },
    "/sitemap.txt": { redirect: { to: "/sitemap_index.xml", statusCode: 301 } },
    "/_nuxt/**": {
      headers: { "cache-control": "public, max-age=31536000, immutable" },
    },
    "/fonts/**": {
      headers: { "cache-control": "public, max-age=31536000, immutable" },
    },
    "/favicon.ico": {
      headers: { "cache-control": "public, max-age=604800" },
    },
    "/favicon.svg": {
      headers: { "cache-control": "public, max-age=604800" },
    },
    "/favicon-96x96.png": {
      headers: { "cache-control": "public, max-age=604800" },
    },
    "/apple-touch-icon.png": {
      headers: { "cache-control": "public, max-age=604800" },
    },
    "/site.webmanifest": {
      headers: { "cache-control": "public, max-age=604800" },
    },
  },
  $production: {
    scripts: {
      registry: {
        plausibleAnalytics: {
          domain: "cold.global",
          trigger: "onNuxtReady",
        },
      },
    },
  },
  typescript: {
    typeCheck: false,
  },
  vite: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    plugins: [tailwindcss() as any],
    // Suppress OpenTelemetry 'this' keyword warnings (ESM compatibility)
    optimizeDeps: {
      include: [
        "@vue/devtools-core",
        "@vue/devtools-kit",
        "@tanstack/vue-query-devtools",
        "@tanstack/vue-query",
        "mitt",
        "openapi-fetch",
        "date-fns",
        "@vue-leaflet/vue-leaflet",
        "zod",
        "v-calendar",
      ],
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
      additionalOrigins: process.env.NUXT_ADDITIONAL_ORIGINS,
    },
  },
  site: {
    url: process.env.NUXT_SITE_URL,
    name: process.env.NUXT_SITE_NAME || "Choice of Law Dataverse",
  },
  sitemap: {
    exclude: SITEMAP_EXCLUDE,
    defaults: { changefreq: "monthly", priority: 0.5 },
    sitemaps: {
      pages: {
        includeAppSources: true,
        exclude: SITEMAP_EXCLUDE,
        defaults: { changefreq: "weekly", priority: 0.7 },
      },
      ...ENTITY_SITEMAPS,
    },
  },
  robots: {
    robotsTxt: true,
    sitemap: ["/sitemap_index.xml"],
    groups: [
      {
        userAgent: ["*"],
        allow: ["/"],
        disallow: NON_PUBLIC_PATHS,
        contentSignal: CONTENT_SIGNAL,
        comment: [
          "CoLD content is licensed CC BY 4.0 — reuse requires attribution.",
          "Machine-readable resources: /.well-known/api-catalog",
        ],
      },
      {
        userAgent: AI_TRAINING_CRAWLERS,
        disallow: ["/"],
        contentSignal: { "ai-train": "no" },
        comment: [
          "Crawlers that collect content for model training. AI assistants",
          "fetching pages for a user are allowed by the group above.",
        ],
      },
    ],
  },
  colorMode: {
    preference: "light",
  },
  ui: {
    fonts: false,
  },
  fonts: {
    families: [
      {
        name: "DM Sans",
        weight: "400",
        preload: true,
        src: "/fonts/dm-sans-latin-400-normal.woff2",
      },
      {
        name: "DM Sans",
        weight: "500",
        src: "/fonts/dm-sans-latin-500-normal.woff2",
      },
      {
        name: "DM Sans",
        weight: "600",
        src: "/fonts/dm-sans-latin-600-normal.woff2",
      },
      {
        name: "DM Sans",
        weight: "700",
        src: "/fonts/dm-sans-latin-700-normal.woff2",
      },
      {
        name: "IBM Plex Mono",
        weight: "400",
        src: "/fonts/ibm-plex-mono-latin-400-normal.woff2",
      },
    ],
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
  },
});
