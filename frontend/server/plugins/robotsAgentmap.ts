import { AI_CATALOG_PATH } from "../utils/aiCatalog";

const END_MARKER = "# END nuxt-robots";

/**
 * Advertises the ARD manifest from robots.txt.
 *
 * `@nuxtjs/robots` has no option for the `Agentmap` directive, so it is
 * appended through the module's own output hook rather than by taking over the
 * route. The line goes inside the module's markers, next to `Sitemap`, so the
 * generated block stays contiguous.
 */
export default defineNitroPlugin((nitroApp) => {
  const config = useRuntimeConfig();
  const siteUrl = String(config.public.siteUrl ?? "").replace(/\/+$/, "");

  if (!siteUrl) return;

  const directive = `Agentmap: ${siteUrl}${AI_CATALOG_PATH}`;

  nitroApp.hooks.hook("robots:robots-txt", (ctx: { robotsTxt: string }) => {
    ctx.robotsTxt = ctx.robotsTxt.includes(END_MARKER)
      ? ctx.robotsTxt.replace(END_MARKER, `${directive}\n${END_MARKER}`)
      : `${ctx.robotsTxt}\n${directive}\n`;
  });
});
