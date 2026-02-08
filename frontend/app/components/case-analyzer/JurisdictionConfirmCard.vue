<template>
  <UCard>
    <template #header>
      <div class="card-header-modern">
        <div class="card-header-modern__text">
          <h3>Confirm Jurisdiction</h3>
          <p>Verify detected location</p>
        </div>
      </div>
    </template>

    <div v-if="jurisdictionInfo" class="space-y-6">
      <DocumentDisplay :document-name="documentName" />

      <UFormField label="Legal System Type">
        <USelect
          :model-value="jurisdictionInfo.legal_system_type"
          :items="legalSystemOptions"
          placeholder="Select legal system"
          size="xl"
          class="w-full"
          :disabled="isLoading"
          @update:model-value="
            (value) => handleLegalSystemUpdate(value as string)
          "
        />
      </UFormField>

      <UFormField label="Jurisdiction">
        <div v-if="jurisdictionsLoading" class="text-sm text-gray-500">
          Loading jurisdictions...
        </div>
        <div v-else-if="jurisdictionsError" class="text-sm text-gray-500">
          Failed to load jurisdictions
        </div>
        <JurisdictionSelectMenu
          v-else
          :model-value="selectedJurisdiction"
          :jurisdictions="jurisdictions || []"
          placeholder="Select jurisdiction"
          @update:model-value="handleJurisdictionUpdate"
          @jurisdiction-selected="handleJurisdictionSelected"
        />
      </UFormField>
    </div>

    <template #footer>
      <div class="card-footer-modern">
        <p class="card-footer-modern__hint">
          <UIcon name="i-heroicons-arrow-path" />
          You can adjust later
        </p>
        <div class="card-footer-modern__actions">
          <UButton variant="ghost" color="neutral" @click="$emit('reset')">
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
import { computed } from "vue";
import type { JurisdictionInfo, JurisdictionOption } from "~/types/analyzer";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import DocumentDisplay from "@/components/case-analyzer/DocumentDisplay.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

const {
  data: jurisdictions,
  isLoading: jurisdictionsLoading,
  error: jurisdictionsError,
} = useJurisdictions();

const props = defineProps<{
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
  "legal-system-updated": [legalSystemType: string];
}>();

const legalSystemOptionsBase = [
  "Civil-law jurisdiction",
  "Common-law jurisdiction",
  "No court decision",
];

const legalSystemOptions = computed(() => {
  const options = [...legalSystemOptionsBase];
  const current = props.jurisdictionInfo?.legal_system_type;
  if (current && !options.includes(current)) {
    options.push(current);
  }
  return options;
});

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

function handleLegalSystemUpdate(legalSystemType: string | undefined) {
  if (legalSystemType) {
    emit("legal-system-updated", legalSystemType);
  }
}
</script>
