<template>
  <section class="sub-notes" aria-label="Submission notes">
    <div class="sub-notes__decor" aria-hidden="true">
      <div class="sub-notes__orb sub-notes__orb--purple" />
      <div class="sub-notes__orb sub-notes__orb--green" />
      <div class="sub-notes__grain" />
    </div>

    <header class="sub-notes__header">
      <span class="sub-notes__eyebrow">
        <span class="sub-notes__bullet" aria-hidden="true" />
        Before you submit
      </span>
      <span class="sub-notes__counter" aria-hidden="true">
        <span class="sub-notes__counter-num">{{ counterNum }}</span>
        <span class="sub-notes__counter-label">{{ counterLabel }}</span>
      </span>
    </header>

    <div class="sub-notes__list" role="list">
      <component
        :is="note.to ? NuxtLink : 'div'"
        v-for="(note, idx) in resolvedNotes"
        :key="`${idx}-${note.title}`"
        :to="note.to"
        role="listitem"
        :class="['sub-notes__item', { 'sub-notes__item--link': !!note.to }]"
      >
        <span
          :class="[
            'sub-notes__icon',
            `sub-notes__icon--${note.variant ?? 'purple'}`,
          ]"
          aria-hidden="true"
        >
          <UIcon :name="note.icon" />
        </span>
        <div class="sub-notes__body">
          <div class="sub-notes__lede">
            <span class="sub-notes__index" aria-hidden="true">
              {{ String(idx + 1).padStart(2, "0") }}
            </span>
            <h3 class="sub-notes__title">{{ note.title }}</h3>
            <span v-if="note.badge" class="sub-notes__badge">
              <svg
                class="sub-notes__badge-icon"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  d="M12 2L13.09 8.26L19 9L13.09 9.74L12 16L10.91 9.74L5 9L10.91 8.26L12 2Z"
                />
              </svg>
              {{ note.badge }}
            </span>
          </div>
          <p v-if="note.description" class="sub-notes__text">
            {{ note.description }}
          </p>
        </div>
        <span v-if="note.to" class="sub-notes__cta" aria-hidden="true">
          <UIcon name="i-material-symbols:arrow-outward" />
        </span>
      </component>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, resolveComponent } from "vue";

const NuxtLink = resolveComponent("NuxtLink");

export interface SubmissionNote {
  icon: string;
  variant?: "purple" | "green" | "teal";
  title: string;
  description?: string;
  to?: string;
  badge?: string;
}

const props = withDefaults(
  defineProps<{
    showAutosaveNote?: boolean;
    extraNotes?: SubmissionNote[];
  }>(),
  {
    showAutosaveNote: true,
    extraNotes: () => [],
  },
);

const TERMS_NOTE: SubmissionNote = {
  icon: "i-material-symbols:scale-outline",
  variant: "purple",
  title: "Submission terms",
  description:
    "Please ensure you have the necessary rights and permissions before submitting any content. All submissions are subject to review and may be edited for clarity and consistency.",
};

const AUTOSAVE_NOTE: SubmissionNote = {
  icon: "i-material-symbols:save-clock-outline",
  variant: "green",
  title: "No autosave",
  description:
    "Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.",
};

const resolvedNotes = computed<SubmissionNote[]>(() => {
  const list: SubmissionNote[] = [TERMS_NOTE];
  if (props.showAutosaveNote) list.push(AUTOSAVE_NOTE);
  list.push(...props.extraNotes);
  return list;
});

const counterNum = computed(() =>
  String(resolvedNotes.value.length).padStart(2, "0"),
);
const counterLabel = computed(() =>
  resolvedNotes.value.length === 1 ? "note" : "notes",
);
</script>

<style scoped>
.sub-notes {
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
  border-radius: 1rem;
  padding: 1.125rem 1.125rem 1.25rem;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-cold-cream) 38%, white),
    color-mix(in srgb, white 96%, var(--color-cold-purple))
  );
  border: 1px solid
    color-mix(in srgb, var(--color-cold-purple) 16%, transparent);
  box-shadow: 0 1px 2px 0 rgb(15 0 53 / 0.04);
}

@media (min-width: 768px) {
  .sub-notes {
    padding: 1.375rem 1.625rem 1.5rem;
  }
}

/* Decorative atmosphere */
.sub-notes__decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: inherit;
}

.sub-notes__orb {
  position: absolute;
  width: 14rem;
  height: 14rem;
  border-radius: 9999px;
  filter: blur(64px);
  opacity: 0.55;
}

.sub-notes__orb--purple {
  top: -5rem;
  left: -3.5rem;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--color-cold-purple) 28%, transparent),
    transparent 70%
  );
}

.sub-notes__orb--green {
  bottom: -5rem;
  right: -3.5rem;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--color-cold-green) 38%, transparent),
    transparent 70%
  );
}

.sub-notes__grain {
  position: absolute;
  inset: 0;
  opacity: 0.18;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
}

/* Header band */
.sub-notes__header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.875rem;
  margin-bottom: 0.25rem;
  border-bottom: 1px dashed
    color-mix(in srgb, var(--color-cold-night) 14%, transparent);
}

.sub-notes__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.6875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--color-cold-night);
}

.sub-notes__bullet {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-cold-purple) 14%, white);
}

.sub-notes__counter {
  display: inline-flex;
  align-items: baseline;
  gap: 0.375rem;
  font-family: "IBM Plex Mono", monospace;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--color-cold-night-alpha);
}

.sub-notes__counter-num {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-cold-night);
  font-feature-settings: "tnum";
}

.sub-notes__counter-label {
  font-size: 0.625rem;
}

/* Notes list */
.sub-notes__list {
  position: relative;
  list-style: none;
  margin: 0;
  padding: 0;
}

.sub-notes__item {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: flex-start;
  gap: 0.875rem;
  padding: 1rem 0;
  text-decoration: none;
  color: inherit;
}

.sub-notes__item + .sub-notes__item {
  border-top: 1px solid
    color-mix(in srgb, var(--color-cold-night) 6%, transparent);
}

@media (min-width: 768px) {
  .sub-notes__item {
    gap: 1.125rem;
    padding: 1.125rem 0;
  }
}

/* Linked notes get an interactive lift */
.sub-notes__item--link {
  cursor: pointer;
  margin-left: -0.625rem;
  margin-right: -0.625rem;
  padding-left: 0.625rem;
  padding-right: 0.625rem;
  border-radius: 0.625rem;
  transition:
    background 180ms ease,
    transform 180ms ease;
}

.sub-notes__item--link:hover {
  background: color-mix(in srgb, white 60%, var(--color-cold-purple) 4%);
}

.sub-notes__item--link:hover .sub-notes__cta {
  transform: translate(2px, -2px);
  color: var(--color-cold-purple);
}

.sub-notes__item--link:focus-visible {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
}

/* Icon tile */
.sub-notes__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.625rem;
  font-size: 1.125rem;
  border: 1px solid transparent;
  position: relative;
  align-self: flex-start;
  margin-top: 1px;
}

.sub-notes__icon::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 1px 0 0 rgb(255 255 255 / 0.8);
  pointer-events: none;
}

.sub-notes__icon--purple {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 16%, white),
    color-mix(in srgb, var(--color-cold-purple) 6%, white)
  );
  border-color: color-mix(in srgb, var(--color-cold-purple) 24%, transparent);
  color: var(--color-cold-purple);
}

.sub-notes__icon--green {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-green) 24%, white),
    color-mix(in srgb, var(--color-cold-teal) 12%, white)
  );
  border-color: color-mix(in srgb, var(--color-cold-green) 32%, transparent);
  color: color-mix(
    in srgb,
    var(--color-cold-teal) 90%,
    var(--color-cold-night)
  );
}

.sub-notes__icon--teal {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-teal) 18%, white),
    color-mix(in srgb, var(--color-cold-purple) 6%, white)
  );
  border-color: color-mix(in srgb, var(--color-cold-teal) 28%, transparent);
  color: var(--color-cold-teal);
}

/* Body */
.sub-notes__body {
  min-width: 0;
}

.sub-notes__lede {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.625rem;
  margin-bottom: 0.25rem;
}

.sub-notes__index {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--color-cold-purple);
  font-feature-settings: "tnum";
  flex-shrink: 0;
}

.sub-notes__title {
  font-family: "DM Sans", sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.005em;
  color: var(--color-cold-night);
  margin: 0;
}

.sub-notes__badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-family: "DM Sans", sans-serif;
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: white;
  background-image: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-teal)
  );
  box-shadow: 0 2px 6px -2px
    color-mix(in srgb, var(--color-cold-purple) 50%, transparent);
}

.sub-notes__badge-icon {
  width: 0.625rem;
  height: 0.625rem;
}

.sub-notes__text {
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--color-cold-night-alpha);
  margin: 0;
  max-width: 64ch;
  text-wrap: pretty;
}

.sub-notes__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  color: var(--color-cold-night-alpha);
  background: color-mix(in srgb, var(--color-cold-purple) 8%, white);
  border: 1px solid
    color-mix(in srgb, var(--color-cold-purple) 16%, transparent);
  align-self: center;
  transition:
    transform 180ms ease,
    color 180ms ease,
    background 180ms ease;
}

/* Entrance choreography */
@media (prefers-reduced-motion: no-preference) {
  .sub-notes {
    animation: subNotesEnter 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .sub-notes__item {
    animation: subNotesItemEnter 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .sub-notes__item:nth-child(1) {
    animation-delay: 120ms;
  }
  .sub-notes__item:nth-child(2) {
    animation-delay: 200ms;
  }
  .sub-notes__item:nth-child(3) {
    animation-delay: 280ms;
  }
  .sub-notes__item:nth-child(4) {
    animation-delay: 360ms;
  }
}

@keyframes subNotesEnter {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes subNotesItemEnter {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .sub-notes__header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .sub-notes__counter {
    margin-left: auto;
  }

  .sub-notes__icon {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
    border-radius: 0.5rem;
  }
}
</style>
