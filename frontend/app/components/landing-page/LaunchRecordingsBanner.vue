<template>
  <NuxtLink :to="LAUNCH_EVENT_PATH" class="launch-banner">
    <img
      :src="youTubeThumbnailUrl(LAUNCH_EVENT_RECORDINGS.overview.videoId)"
      alt=""
      loading="lazy"
      decoding="async"
      class="launch-banner__thumb"
    />

    <div class="launch-banner__body">
      <span class="launch-banner__eyebrow">
        <Icon
          name="i-material-symbols:play-circle-outline"
          class="launch-banner__eyebrow-icon"
        />
        Launch event &middot; {{ LAUNCH_EVENT_DATE }}
      </span>
      <h2 class="launch-banner__title">Watch the launch event recordings</h2>
      <p class="launch-banner__lead">
        {{ LAUNCH_EVENT_RECORDING_COUNT }} sessions on party autonomy, the HCCH
        Principles, and using the Dataverse for research.
      </p>
    </div>

    <span class="launch-banner__cta">
      Watch now
      <Icon
        name="i-material-symbols:arrow-forward-rounded"
        class="launch-banner__cta-arrow"
      />
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
import {
  LAUNCH_EVENT_DATE,
  LAUNCH_EVENT_PATH,
  LAUNCH_EVENT_RECORDING_COUNT,
  LAUNCH_EVENT_RECORDINGS,
  youTubeThumbnailUrl,
} from "@/config/launchEvent";
</script>

<style scoped>
@reference "@/assets/styles.css";

.launch-banner {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-radius: 1rem;
  text-decoration: none;
  background: linear-gradient(
    120deg,
    color-mix(in srgb, var(--color-cold-purple) 8%, white),
    color-mix(in srgb, var(--color-cold-teal) 7%, white) 70%,
    white
  );
  border: 1px solid
    color-mix(in srgb, var(--color-cold-purple) 14%, transparent);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

@media (min-width: 768px) {
  .launch-banner {
    flex-direction: row;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem 1.5rem;
  }
}

.launch-banner:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--color-cold-purple) 38%, transparent);
  box-shadow: 0 8px 24px -12px
    color-mix(in srgb, var(--color-cold-purple) 45%, transparent);
}

.launch-banner__thumb {
  flex-shrink: 0;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 0.75rem;
  border: 1px solid color-mix(in srgb, var(--color-cold-night) 10%, transparent);
}

@media (min-width: 768px) {
  .launch-banner__thumb {
    width: 10rem;
  }
}

.launch-banner__body {
  flex: 1;
  min-width: 0;
}

.launch-banner__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: "DM Sans", sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
}

.launch-banner__eyebrow-icon {
  font-size: 1rem;
  color: var(--color-cold-purple);
}

.launch-banner__title {
  font-family: "DM Sans", sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--color-cold-night);
  margin-top: 0.375rem;
  text-wrap: balance;
}

.launch-banner__lead {
  margin-top: 0.375rem;
  max-width: 40rem;
  font-family: "DM Sans", sans-serif;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-cold-night-alpha);
}

.launch-banner__cta {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-family: "DM Sans", sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-cold-purple);
}

.launch-banner__cta-arrow {
  font-size: 1.125rem;
  transition: transform 180ms ease;
}

.launch-banner:hover .launch-banner__cta-arrow {
  transform: translateX(3px);
}

@media (prefers-reduced-motion: reduce) {
  .launch-banner,
  .launch-banner__cta-arrow {
    transition: none;
  }

  .launch-banner:hover {
    transform: none;
  }

  .launch-banner:hover .launch-banner__cta-arrow {
    transform: none;
  }
}
</style>
