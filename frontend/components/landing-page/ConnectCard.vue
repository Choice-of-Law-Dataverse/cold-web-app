<template>
  <UCard
    :ui="cardUi"
    class="cold-ucard h-full"
    :style="cardHeight ? { height: cardHeight } : undefined"
  >
    <template #header>
      <h2 class="popular-title">{{ title }}</h2>
      <p v-if="subtitle" class="result-value-small text-center px-2">
        {{ subtitle }}
      </p>
    </template>

    <!-- Middle section (body) grows to fill available space -->
    <div
      ref="iconContainerEl"
      class="middle flex-1 min-h-0 flex flex-col items-center justify-center"
    >
      <div class="icon-container">
        <a
          :href="buttonLink"
          :target="newTab ? '_blank' : '_self'"
          :rel="newTab ? 'noopener noreferrer' : ''"
        >
          <template v-if="imageSrc">
            <img :src="imageSrc" alt="" />
          </template>
          <template v-else>
            <Icon
              :name="iconName"
              class="icon-media"
              :size="computedIconSize"
              :style="{ color: 'var(--color-cold-green)' }"
            />
          </template>
        </a>
      </div>
    </div>

    <template #footer>
      <div class="link-container">
        <a
          :href="buttonLink"
          :target="newTab ? '_blank' : '_self'"
          :rel="newTab ? 'noopener noreferrer' : ''"
        >
          <UButton
            class="suggestion-button"
            variant="link"
            :icon="buttonIcon"
            trailing
          >
            {{ buttonText }}
          </UButton>
        </a>
      </div>
    </template>
  </UCard>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  cardHeight: {
    type: String,
    required: false,
    default: '',
  },
  subtitle: {
    type: String,
    required: false,
    default: '',
  },
  buttonText: {
    type: String,
    required: true,
  },
  buttonLink: {
    type: String,
    required: true,
  },
  iconName: {
    type: String,
    required: false,
    default: '',
  },
  imageSrc: {
    type: String,
    required: false,
    default: '',
  },
  newTab: {
    type: Boolean,
    default: true,
  },
  buttonIcon: {
    type: String,
    required: false,
  },
})

const iconContainerEl = ref(null)
const measuredMiddleHeight = ref(0)

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n))
}

onMounted(() => {
  if (!iconContainerEl.value) return
  const ro = new ResizeObserver((entries) => {
    for (const entry of entries) {
      measuredMiddleHeight.value = entry.contentRect.height || 0
    }
  })
  ro.observe(iconContainerEl.value)
  onBeforeUnmount(() => ro.disconnect())
})

const computedIconSize = computed(() => {
  if (measuredMiddleHeight.value > 0) {
    // Use 70% of available middle height, clamped to keep it tidy
    return clamp(Math.floor(measuredMiddleHeight.value * 0.7), 64, 200)
  }
  // Fallback: derive from provided cardHeight if any
  const m = /([0-9.]+)px/.exec(props.cardHeight || '')
  if (m) {
    const h = parseFloat(m[1]) || 0
    return clamp(Math.floor(h * 0.45), 64, 200)
  }
  return 120
})
const cardUi = {
  base: 'h-full flex flex-col border-0 shadow-none ring-0',
  divide: 'divide-y-0',
  header: { base: 'border-none' },
  body: { base: 'flex-1 min-h-0 flex flex-col' },
  footer: { base: 'mt-auto border-none' },
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 2px;
}

.middle {
  /* grows within card body */
  display: flex;
}

.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  flex: 1;
}

.icon-container img {
  max-height: 100px;
  width: auto;
  height: auto;
}

/* Let Icon component control final size via :size */
.icon-container :deep(svg) {
  width: auto;
  height: auto;
  max-height: none;
}

.icon-media {
  display: inline-flex;
}

.link-container {
  display: flex;
  justify-content: center;
}

.result-value-small {
  line-height: 36px !important;
  margin-top: 0px !important;
  margin-bottom: 0px !important;
}
</style>
