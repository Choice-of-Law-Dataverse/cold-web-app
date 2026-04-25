<template>
  <EntityContent base-path="/jurisdiction" :data="data">
    <template #name="{ value, label }">
      <DetailRow :label="label">
        <div class="report-block">
          <h2 class="report-block__title">{{ value }}</h2>
          <div v-if="data.coldId || legalFamily" class="report-block__subtitle">
            <JurisdictionFlag
              v-if="data.coldId"
              :iso3="data.coldId"
              class="report-block__flag"
            />
            <span v-if="legalFamily">{{ legalFamily }}</span>
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

const legalFamily = computed(() => {
  const value = props.data?.legalFamily;
  if (!value || value === "N/A") return "";
  return String(value);
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
</style>
