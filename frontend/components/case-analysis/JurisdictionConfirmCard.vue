<template>
  <UCard>
    <template #header>
      <div class="card-header-modern">
        <div class="icon-badge icon-badge--teal-green">
          <UIcon name="i-heroicons-globe-alt" class="icon" />
        </div>
        <div class="card-header-modern__text">
          <h3>Confirm Jurisdiction</h3>
          <p>Verify detected location</p>
        </div>
      </div>
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
      <div class="card-footer-modern">
        <p class="card-footer-modern__hint">
          <UIcon name="i-heroicons-arrow-path" />
          You can adjust later
        </p>
        <div class="card-footer-modern__actions">
          <UButton variant="ghost" color="gray" @click="$emit('reset')">
            Start Over
          </UButton>
          <UButton
            class="btn-primary-gradient"
            :loading="isLoading"
            @click="$emit('continue')"
          >
            <template #leading>
              <UIcon name="i-heroicons-arrow-right" class="h-4 w-4" />
            </template>
            Continue Analysis
          </UButton>
        </div>
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
