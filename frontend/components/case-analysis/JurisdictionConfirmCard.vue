<template>
  <UCard>
    <template #header>
      <h3 class="font-semibold">Confirm Jurisdiction</h3>
    </template>

    <div v-if="jurisdictionInfo" class="space-y-6">
      <UFormGroup label="Legal System Type">
        <UInput :model-value="jurisdictionInfo.legal_system_type" readonly />
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
          color="primary"
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

defineProps<{
  jurisdictionInfo: JurisdictionInfo | null;
  selectedJurisdiction: JurisdictionOption | undefined;
  jurisdictions: JurisdictionOption[] | null;
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
