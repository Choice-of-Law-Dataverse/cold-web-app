<template>
  <div class="mt-4">
    <ScriptYouTubePlayer
      :video-id="videoId"
      :player-vars="{ autoplay: 0, playsinline: 1, rel: 0, modestbranding: 1 }"
      :root-attrs="rootAttrs"
    >
      <template #placeholder="{ placeholder }">
        <img
          :src="thumbnailFailed ? fallbackThumbnail : placeholder"
          :alt="`Watch the recording: ${title}`"
          loading="lazy"
          class="absolute inset-0 size-full object-cover"
          @error="thumbnailFailed = true"
        />
        <span
          class="pointer-events-none absolute inset-0 flex items-center justify-center"
        >
          <span
            class="bg-cold-purple flex h-12 w-16 items-center justify-center"
          >
            <UIcon name="i-heroicons-play-solid" class="size-6 text-white" />
          </span>
        </span>
      </template>
    </ScriptYouTubePlayer>

    <a
      :href="`https://www.youtube.com/watch?v=${videoId}`"
      target="_blank"
      rel="noopener noreferrer"
      :aria-label="`Watch ${title} on YouTube (opens in new tab)`"
      class="text-cold-purple mt-2 inline-flex items-center gap-1.5 text-xs font-medium tracking-wide"
    >
      <UIcon name="i-heroicons-arrow-top-right-on-square" class="size-3.5" />
      Watch on YouTube
    </a>
  </div>
</template>

<script setup lang="ts">
interface Props {
  videoId: string;
  title: string;
}

const props = defineProps<Props>();

const thumbnailFailed = ref(false);
const fallbackThumbnail = computed(
  () => `https://i.ytimg.com/vi/${props.videoId}/hqdefault.jpg`,
);
const rootAttrs = computed(() => ({
  class: "border-cold-gray border",
  "aria-label": `Play the recording: ${props.title}`,
}));
</script>
