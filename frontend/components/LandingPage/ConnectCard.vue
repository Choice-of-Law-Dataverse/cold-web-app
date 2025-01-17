<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="icon-container">
      <a :href="links.substack" target="_blank" rel="noopener noreferrer">
        <Icon name="i-bi:substack" size="96" style="color: #ff6719" />
      </a>
    </div>
    <div class="link-container">
      <a :href="links.substack" target="_blank" rel="noopener noreferrer">
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          Subscribe on Substack
        </UButton>
      </a>
    </div>
  </UCard>
</template>

<script setup>
import { externalLinks } from '~/utils/externalLinks'

// Define props
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
})

// Data variables
const links = externalLinks
</script>

<style scoped>
h2 {
  text-align: center;
}

.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 32px;
}

.link-container {
  display: flex;
  justify-content: center;
}
</style>
