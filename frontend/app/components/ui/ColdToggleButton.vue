<template>
  <ColdControlShell
    v-bind="$attrs"
    :label="label"
    :disabled="disabled"
    :pressed="pressed"
    class="cold-toggle-btn-wrap"
    @click="emit('click', $event)"
  >
    <slot />
  </ColdControlShell>
</template>

<script setup lang="ts">
import ColdControlShell from "@/components/ui/ColdControlShell.vue";

defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    label?: string;
    disabled?: boolean;
    pressed?: boolean;
  }>(),
  {
    label: undefined,
    disabled: false,
    pressed: undefined,
  },
);

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();
</script>

<style>
.cold-toggle-btn-wrap {
  justify-content: center;
}
</style>
