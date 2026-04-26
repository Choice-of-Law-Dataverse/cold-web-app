<template>
  <LandingCardShell
    title="Stay Connected"
    subtitle="Reach out and follow updates from CoLD"
    header-class="text-left"
  >
    <UButton
      v-for="channel in channels"
      :key="channel.label"
      :to="channel.href"
      :target="channel.external ? '_blank' : undefined"
      :rel="channel.external ? 'noopener noreferrer' : undefined"
      variant="soft"
      color="neutral"
      class="connect-row"
    >
      <span class="connect-icon-tile">
        <Icon :name="channel.icon" class="connect-icon" />
      </span>
      <span class="connect-text">
        <span class="connect-label">{{ channel.label }}</span>
        <span class="connect-meta">{{ channel.meta }}</span>
      </span>
      <Icon
        :name="
          channel.external
            ? 'i-material-symbols:open-in-new'
            : 'i-material-symbols:arrow-forward-rounded'
        "
        class="connect-arrow"
      />
    </UButton>
  </LandingCardShell>
</template>

<script setup lang="ts">
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";
import { externalLinks } from "@/utils/externalLinks";

interface Channel {
  label: string;
  meta: string;
  icon: string;
  href: string;
  external: boolean;
}

const channels: Channel[] = [
  {
    label: "Questions or Feedback",
    meta: "Get in touch with the team",
    icon: "i-material-symbols:alternate-email",
    href: "/contact",
    external: false,
  },
  {
    label: "CoLD Newsletter",
    meta: "Subscribe on Substack",
    icon: "i-simple-icons:substack",
    href: externalLinks.substack,
    external: true,
  },
  {
    label: "CoLD on LinkedIn",
    meta: "Follow updates and announcements",
    icon: "i-simple-icons:linkedin",
    href: externalLinks.linkedin,
    external: true,
  },
  {
    label: "CoLD on GitHub",
    meta: "Browse the open-source code",
    icon: "i-simple-icons:github",
    href: externalLinks.github,
    external: true,
  },
];
</script>

<style scoped>
.connect-row {
  align-items: center;
}

.connect-icon-tile {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 0.625rem;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 12%, transparent),
    color-mix(in srgb, var(--color-cold-green) 16%, transparent)
  );
  color: var(--color-cold-purple);
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.connect-row:hover .connect-icon-tile {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 20%, transparent),
    color-mix(in srgb, var(--color-cold-green) 24%, transparent)
  );
  transform: rotate(-3deg);
}

.connect-icon {
  font-size: 1.125rem;
}

.connect-text {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  text-align: left;
  gap: 0.125rem;
  min-width: 0;
}

.connect-row .connect-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.25;
  letter-spacing: 0.005em;
}

.connect-row .connect-meta {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--color-cold-slate);
  line-height: 1.3;
  letter-spacing: 0.01em;
}

.connect-arrow {
  flex-shrink: 0;
  font-size: 0.9375rem;
  color: color-mix(in srgb, var(--color-cold-night) 35%, transparent);
  transition:
    transform 0.2s ease,
    color 0.2s ease;
}

.connect-row:hover .connect-arrow {
  color: var(--color-cold-purple);
  transform: translateX(2px);
}

@media (prefers-reduced-motion: reduce) {
  .connect-row:hover .connect-icon-tile,
  .connect-row:hover .connect-arrow {
    transform: none;
  }
}
</style>
