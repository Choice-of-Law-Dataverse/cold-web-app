<template>
  <div
    class="border-cold-gray grid grid-cols-[100px_1fr] gap-x-8 border-b py-6"
    :class="{
      'border-b-0 pb-1': last,
      'pt-1': first,
    }"
  >
    <div
      class="text-cold-purple pt-0.5 text-sm leading-snug font-medium tracking-wide"
    >
      {{ time }}
    </div>
    <div>
      <span
        v-if="tag"
        class="mb-2 inline-block px-2.5 py-0.5 text-[10px] font-medium tracking-[1.5px] text-white uppercase"
        :class="specialTag ? 'bg-cold-purple' : 'bg-cold-night'"
      >
        {{ tag }}
      </span>
      <h3
        class="text-cold-night mb-1.5 font-serif text-lg leading-snug font-bold"
      >
        {{ title }}
      </h3>
      <div class="text-cold-charcoal text-sm leading-relaxed font-light">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  time: string;
  title: string;
  tag?: string;
  specialTag?: boolean;
  last?: boolean;
  first?: boolean;
}

withDefaults(defineProps<Props>(), {
  tag: undefined,
  specialTag: false,
  last: false,
  first: false,
});
</script>
