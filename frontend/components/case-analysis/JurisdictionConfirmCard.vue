<template>
  <UCard>
    <template #header>
      <h3 class="font-semibold">Confirm Jurisdiction</h3>
    </template>

    <div v-if="jurisdictionInfo" class="space-y-6">
      <DocumentDisplay :document-name="documentName" />

      <UFormGroup label="Legal System Type">
        <UInput
          :model-value="jurisdictionInfo.legal_system_type"
          :readonly="true"
        />
        <template #hint>
          <span
            v-if="jurisdictionInfo.confidence"
            class="text-xs text-cold-teal"
          >
            {{ jurisdictionInfo.confidence }} confidence
          </span>
        </template>
      </UFormGroup>

      <UFormGroup label="Jurisdiction">
        <JurisdictionSelectMenu
          :model-value="selectedJurisdiction"
          :countries="jurisdictions || []"
          placeholder="Select jurisdiction"
          @update:model-value="handleJurisdictionUpdate"
          @country-selected="handleJurisdictionSelected"
        />
      </UFormGroup>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <UButton variant="ghost" color="gray" @click="$emit('reset')">
          Start Over
        </UButton>
        <UButton
          class="bg-cold-purple text-white hover:bg-cold-purple/90"
          :loading="isLoading"
          @click="$emit('continue')"
        >
          Continue Analysis
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import type { JurisdictionInfo, JurisdictionOption } from "~/types/analyzer";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import DocumentDisplay from "@/components/case-analysis/DocumentDisplay.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

const { data: jurisdictions } = useJurisdictions();

defineProps<{
  documentName: string;
  jurisdictionInfo: JurisdictionInfo | null;
  selectedJurisdiction: JurisdictionOption | undefined;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  "update:selectedJurisdiction": [jurisdiction: JurisdictionOption | undefined];
  continue: [];
  reset: [];
  "jurisdiction-updated": [jurisdiction: JurisdictionOption];
}>();

function handleJurisdictionUpdate(
  jurisdiction: JurisdictionOption | undefined,
) {
  emit("update:selectedJurisdiction", jurisdiction);
}

function handleJurisdictionSelected(
  jurisdiction: JurisdictionOption | undefined,
) {
  if (jurisdiction) {
    emit("jurisdiction-updated", jurisdiction);
  }
}
</script>
