<script setup lang="ts">
import { aboutNavLinks, learnNavLinks } from "@/config/navigation";
import { externalLinks } from "@/utils/externalLinks";

const user = useUser();

interface SocialLink {
  label: string;
  icon: string;
  href: string;
}

const socials: SocialLink[] = [
  {
    label: "Subscribe to the CoLD Newsletter on Substack",
    icon: "i-simple-icons:substack",
    href: externalLinks.substack,
  },
  {
    label: "Follow CoLD on LinkedIn",
    icon: "i-simple-icons:linkedin",
    href: externalLinks.linkedin,
  },
  {
    label: "Browse the CoLD source code on GitHub",
    icon: "i-simple-icons:github",
    href: externalLinks.github,
  },
];

const currentYear = new Date().getFullYear();
</script>

<template>
  <footer
    class="footer-container min-h-[300px] px-6 pt-6 pb-24 sm:pt-12 md:pb-12"
  >
    <div class="max-w-container mx-auto">
      <!-- Logo and Tagline - horizontal on desktop, stacked on mobile -->
      <div
        class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <!-- Left: Flag + Title -->
        <div class="flex items-center gap-4">
          <img
            src="https://assets.cold.global/assets/cold_flag_footer.svg"
            class="h-12 w-auto sm:h-14"
            alt="Choice of Law Dataverse flag"
          />
          <h2 class="footer-title leading-tight text-pretty">
            Choice of Law Dataverse
          </h2>
        </div>

        <!-- Right: Funding attribution -->
        <p class="leading-snug text-pretty text-gray-300 sm:text-right">
          Funded by the Swiss National Science Foundation
        </p>
      </div>

      <!-- Footer Sitemap - 4 Columns -->
      <div class="footer-border grid grid-cols-1 gap-8 pt-8 md:grid-cols-4">
        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="footer-heading mb-2">About</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in aboutNavLinks"
              :key="link.key"
              :to="link.path"
              class="footer-link"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="footer-heading mb-2">Learn</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in learnNavLinks"
              :key="link.key"
              :to="link.path"
              class="footer-link"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <div
          class="flex flex-row justify-between gap-3 md:flex-col md:justify-start"
        >
          <h3 class="footer-heading mb-2">Resources</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink to="/contact" class="footer-link"> Contact </NuxtLink>
            <NuxtLink to="/search" class="footer-link"> Search </NuxtLink>
            <NuxtLink to="/disclaimer" class="footer-link">
              Disclaimer
            </NuxtLink>
          </div>
        </div>

        <div
          class="flex flex-row justify-between gap-3 md:flex-col md:justify-start"
        >
          <h3 class="footer-heading mb-2">Admin</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <ClientOnly>
              <a
                v-if="user"
                href="/auth/logout"
                class="footer-link cursor-pointer"
              >
                Logout
              </a>
              <a v-else href="/auth/login" class="footer-link cursor-pointer">
                Login
              </a>

              <template #fallback>
                <a href="/auth/login" class="footer-link cursor-pointer">
                  Login
                </a>
              </template>
            </ClientOnly>

            <NuxtLink to="/moderation" class="footer-link">
              Moderation
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Bottom meta strip: Cite & License · Funding · Stay Connected -->
      <div class="footer-border footer-meta mt-10 pt-8">
        <div class="footer-meta__grid">
          <div class="footer-meta__col">
            <h3 class="footer-heading mb-3">Cite &amp; License</h3>
            <p class="footer-meta__line">
              Cite as
              <span class="footer-meta__muted">
                Choice of Law Dataverse ({{ currentYear }}).
              </span>
            </p>
            <p class="footer-meta__line">
              Released under
              <a
                href="https://creativecommons.org/licenses/by-sa/4.0/"
                target="_blank"
                rel="noopener noreferrer"
                class="footer-meta__link"
              >
                CC&nbsp;BY-SA&nbsp;4.0
              </a>
            </p>
            <NuxtLink to="/disclaimer" class="footer-meta__link">
              Citation &amp; data terms →
            </NuxtLink>
          </div>

          <div class="footer-meta__col">
            <h3 class="footer-heading mb-3">Funding &amp; Host</h3>
            <p class="footer-meta__line">
              Swiss National Science Foundation
              <span class="footer-meta__muted">
                Project No.&nbsp;215469 · 2023–2026
              </span>
            </p>
            <p class="footer-meta__line">University of Lucerne</p>
            <NuxtLink to="/about/supporters" class="footer-meta__link">
              All supporters →
            </NuxtLink>
          </div>

          <div class="footer-meta__col">
            <h3 class="footer-heading mb-3">Stay Connected</h3>
            <div class="footer-socials">
              <a
                v-for="social in socials"
                :key="social.label"
                :href="social.href"
                target="_blank"
                rel="noopener noreferrer"
                :aria-label="social.label"
                class="footer-social"
              >
                <Icon :name="social.icon" class="footer-social__icon" />
              </a>
            </div>
            <NuxtLink to="/contact" class="footer-meta__link">
              Contact the team →
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer-meta__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .footer-meta__grid {
    grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 0.9fr);
    gap: 2.5rem;
  }
}

.footer-meta__col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.footer-meta__line {
  font-size: 0.8125rem;
  line-height: 1.55;
  color: color-mix(in srgb, white 88%, transparent);
}

.footer-meta__muted {
  display: block;
  color: color-mix(in srgb, white 60%, transparent);
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

.footer-meta__link {
  font-size: 0.8125rem;
  font-weight: 600;
  color: white;
  text-decoration: none;
  border-bottom: 1px solid color-mix(in srgb, white 30%, transparent);
  align-self: flex-start;
  padding-bottom: 1px;
  transition:
    color 150ms ease,
    border-color 150ms ease;
}

.footer-meta__link:hover {
  color: var(--color-cold-green);
  border-color: var(--color-cold-green);
}

.footer-socials {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.footer-social {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 0.625rem;
  background: color-mix(in srgb, white 6%, transparent);
  border: 1px solid color-mix(in srgb, white 12%, transparent);
  color: color-mix(in srgb, white 85%, transparent);
  transition:
    background 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    transform 180ms ease;
}

.footer-social:hover {
  background: color-mix(in srgb, white 12%, transparent);
  border-color: color-mix(in srgb, var(--color-cold-green) 55%, transparent);
  color: var(--color-cold-green);
  transform: translateY(-1px);
}

.footer-social__icon {
  font-size: 1rem;
}

@media (prefers-reduced-motion: reduce) {
  .footer-social:hover {
    transform: none;
  }
}
</style>
