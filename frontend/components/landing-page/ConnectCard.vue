<template>
  <UCard :ui="cardUi" class="cold-ucard h-full">
    <template #header>
      <h2 class="popular-title">{{ title }}</h2>
      <p v-if="subtitle" class="result-value-small text-center px-2">
        {{ subtitle }}
      </p>
    </template>

    <!-- Middle section (body) grows to fill available space -->
    <div
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
const cardUi = {
  base: 'h-full flex flex-col border-0 shadow-none ring-0',
  divide: 'divide-y-0',
  header: { base: 'border-none pb-0' },
  body: { base: 'flex-1 min-h-0 flex flex-col py-0' },
  footer: { base: 'mt-auto border-none pt-0' },
}

const props = defineProps({
  title: {
    type: String,
    required: true,
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
  margin: 32px;
}

.icon-container img,
.icon-container :deep(svg) {
  max-height: 40px;
  width: auto;
  height: auto;
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
