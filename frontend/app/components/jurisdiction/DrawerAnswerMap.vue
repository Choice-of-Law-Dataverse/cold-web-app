<template>
  <div v-if="isLoading" class="py-2">
    <LoadingBar />
  </div>
  <InlineError v-else-if="error" :error="error" />
  <div
    v-else-if="answersWithJurisdictions.length > 0"
    class="flex flex-col gap-3"
  >
    <div v-for="answer in answersWithJurisdictions" :key="answer">
      <p
        class="mb-1.5 text-xs font-medium tracking-wide text-gray-500 uppercase"
      >
        {{ answer }}
      </p>
      <div class="flex flex-wrap items-center gap-4">
        <EntityLink
          v-for="jurisdiction in answerGroups.get(answer)"
          :key="jurisdiction.code"
          :id="`${jurisdiction.code}${questionSuffix}`"
          :title="jurisdiction.code"
          base-path="/question"
          variant="jurisdiction"
        >
          <div class="flag-wrapper">
            <JurisdictionFlag
              :iso3="jurisdiction.code"
              class="item-flag"
              :alt="jurisdiction.code + ' flag'"
            />
          </div>
          {{ jurisdiction.code }}
        </EntityLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useQuestionJurisdictions } from "@/composables/useQuestionJurisdictions";
import EntityLink from "@/components/ui/EntityLink.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";

const props = defineProps<{
  questionSuffix: string;
}>();

const {
  data: questionData,
  isLoading,
  error,
} = useQuestionJurisdictions(computed(() => props.questionSuffix));

const answerGroups = computed(
  () => questionData.value?.answerGroups ?? new Map(),
);

const answersWithJurisdictions = computed(
  () => questionData.value?.answers ?? [],
);
</script>
