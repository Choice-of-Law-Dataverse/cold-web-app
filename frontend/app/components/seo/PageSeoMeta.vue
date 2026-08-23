<template>
  <div style="display: none" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  useSeoMeta,
  useHead,
  useRoute,
  useRobotsRule,
  useRuntimeConfig,
} from "#imports";
import {
  buildPageTitle,
  buildSeoDescription,
  toCanonicalPath,
} from "@/utils/seo";
import {
  buildBreadcrumbList,
  buildJsonLdGraph,
  type BreadcrumbItem,
  type JsonLdNode,
} from "@/utils/structuredData";

type JsonLdBuilder = (
  siteUrl: string,
  path: string,
) => JsonLdNode | (JsonLdNode | null | undefined)[] | null | undefined;

interface Props {
  titleCandidates: (string | null | undefined)[];
  fallback: string;
  descriptionCandidates?: (string | null | undefined)[];
  descriptionFallback?: string;
  breadcrumbs?: BreadcrumbItem[];
  jsonLd?: JsonLdBuilder | null;
  noindex?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  descriptionCandidates: () => [],
  descriptionFallback: "",
  breadcrumbs: () => [],
  jsonLd: null,
  noindex: false,
});

const route = useRoute();
const config = useRuntimeConfig();

const siteUrl = computed(() => String(config.public.siteUrl ?? ""));
const canonicalPath = computed(() => toCanonicalPath(route.path));

const pageTitle = computed(() =>
  buildPageTitle([...props.titleCandidates, props.fallback], props.fallback),
);

const pageDescription = computed(() =>
  buildSeoDescription(
    props.descriptionCandidates,
    props.descriptionFallback ||
      `${props.fallback} in the Choice of Law Dataverse, an open database on choice of law in international commercial contracts.`,
  ),
);

/**
 * Only ever tightens the rule. Leaving the indexable case to `@nuxtjs/robots`
 * preserves its environment handling — hardcoding "index, follow" here would
 * override the module's automatic noindex on preview deployments.
 */
if (props.noindex) {
  useRobotsRule({ noindex: true, follow: true });
}

const jsonLdGraph = computed(() => {
  const nodes: (JsonLdNode | null | undefined)[] = [];

  const breadcrumbs = buildBreadcrumbList(siteUrl.value, props.breadcrumbs);
  if (breadcrumbs) nodes.push(breadcrumbs);

  const built = props.jsonLd?.(siteUrl.value, canonicalPath.value);
  if (Array.isArray(built)) nodes.push(...built);
  else if (built) nodes.push(built);

  if (nodes.length === 0) return null;
  return JSON.stringify(buildJsonLdGraph(nodes));
});

useSeoMeta({
  title: pageTitle,
  description: pageDescription,
  ogTitle: pageTitle,
  ogDescription: pageDescription,
  ogType: "article",
  twitterTitle: pageTitle,
  twitterDescription: pageDescription,
});

useHead({
  script: computed(() =>
    jsonLdGraph.value
      ? [
          {
            key: "page-json-ld",
            type: "application/ld+json",
            innerHTML: jsonLdGraph.value,
          },
        ]
      : [],
  ),
});
</script>
