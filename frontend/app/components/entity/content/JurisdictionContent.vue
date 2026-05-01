<template>
  <EntityContent base-path="/jurisdiction" :data="data">
    <template #name="{ value, label }">
      <DetailRow :label="label">
        <div class="report-block">
          <h2 class="report-block__title">{{ value }}</h2>
          <div
            v-if="data.coldId || subtitleTokens.length > 0"
            class="report-block__subtitle"
          >
            <JurisdictionFlag
              v-if="data.coldId"
              :iso3="data.coldId"
              class="report-block__flag"
            />
            <template
              v-for="(token, idx) in subtitleTokens"
              :key="`token-${idx}`"
            >
              <span
                v-if="idx > 0 || data.coldId"
                class="report-block__separator"
                aria-hidden="true"
                >·</span
              >
              <span>{{ token }}</span>
            </template>
          </div>
        </div>
      </DetailRow>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import { computed } from "vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import type { Jurisdiction } from "@/types/entities/jurisdiction";

const props = defineProps<{
  data: Jurisdiction;
}>();

const cleanValue = (value: unknown): string => {
  if (!value) return "";
  const str = String(value);
  if (str === "N/A") return "";
  return str;
};

const subtitleTokens = computed(() => {
  const region = cleanValue(props.data?.region);
  const family = cleanValue(props.data?.legalFamily);
  const familyTokens = family
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
  return [region, ...familyTokens].filter((token) => token.length > 0);
});
</script>

<style scoped>
.report-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.report-block__title {
  font-family: "DM Sans", sans-serif;
  font-weight: 500;
  font-size: clamp(20px, 2.2vw, 24px);
  line-height: 1.25;
  letter-spacing: -0.015em;
  color: var(--color-cold-night);
  margin: 0;
  overflow-wrap: break-word;
}

.report-block__subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  color: var(--color-cold-night-alpha);
}

.report-block__flag {
  height: 12px;
  width: auto;
  display: inline-block;
}

.report-block__separator {
  color: color-mix(in srgb, var(--color-cold-night-alpha) 60%, transparent);
}
</style>
