<template>
  <SearchResultCardContent :result-data="resultData" card-type="Answers">
    <template #answer="{ label, classes }">
      <DetailRow :label="label">
        <div :class="answerClasses(classes)">
          <template v-if="Array.isArray(answerValue)">
            <div class="flex flex-col gap-2">
              <div v-for="(line, i) in answerValue" :key="i">
                {{ line }}
              </div>
            </div>
          </template>
          <template v-else>
            {{ answerValue }}
          </template>
        </div>
      </DetailRow>
    </template>

    <template #moreInformation="{ label }">
      <DetailRow v-if="hasMoreInformation" :label="label">
        <div class="prose mb-2 flex flex-col gap-2">
          <div v-if="resultData.moreInformation">
            {{ resultData.moreInformation }}
          </div>
          <div v-else-if="resultData.oupBookQuote">
            {{ resultData.oupBookQuote }}
          </div>
          <div v-if="relatedCasesCount">
            <NuxtLink class="text-cold-purple" :to="relatedDecisionsLink">
              {{ relatedCasesCount }} related court decisions
            </NuxtLink>
          </div>
        </div>
      </DetailRow>
    </template>

    <template #after-fields>
      <DetailRow v-if="lastUpdatedDisplay" label="Last Updated">
        <div
          class="result-value-small text-sm leading-relaxed whitespace-normal"
        >
          {{ lastUpdatedDisplay }}
        </div>
      </DetailRow>
    </template>
  </SearchResultCardContent>
</template>

<script setup lang="ts">
import { computed } from "vue";
import SearchResultCardContent from "@/components/search-results/SearchResultCardContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { formatYear } from "@/utils/format";

const props = defineProps<{
  resultData: Record<string, unknown>;
}>();

const answerValue = computed(() => {
  const value = props.resultData.answer;
  if (typeof value === "string" && value.includes(",")) {
    return value.split(",").map((part) => part.trim());
  }
  return value || "No answer available";
});

function answerClasses(baseClasses: string[]): string[] {
  const answer = String(props.resultData.answer ?? "");
  const sizeClass =
    answer === "Yes" || answer === "No"
      ? "result-value-large"
      : "result-value-medium";
  return baseClasses.map((c) =>
    c.startsWith("result-value-") ? sizeClass : c,
  );
}

const relatedCasesCount = computed(() => {
  const links = props.resultData.courtDecisionsLink;
  if (!links || typeof links !== "string") return 0;
  return links.split(",").filter((link: string) => link.trim() !== "").length;
});

const relatedDecisionsLink = computed(
  () => `question/${props.resultData.id}#related-court-decisions`,
);

const hasMoreInformation = computed(
  () =>
    (props.resultData.moreInformation &&
      props.resultData.moreInformation !== "") ||
    (props.resultData.oupBookQuote && props.resultData.oupBookQuote !== "") ||
    relatedCasesCount.value > 0,
);

const lastUpdatedDisplay = computed(() => {
  const raw = props.resultData.lastModified || props.resultData.created;
  const y = formatYear(raw as string | null | undefined);
  return y ? String(y) : "";
});
</script>
