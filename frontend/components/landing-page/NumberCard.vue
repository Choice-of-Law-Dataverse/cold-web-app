<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="number-container">
      <span>1311</span>
    </div>
    <div class="link-container">
      <a :href="buttonLink">
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          {{ buttonText }}
        </UButton>
      </a>
    </div>
  </UCard>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true,
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
    required: true,
  },
  newTab: {
    type: Boolean,
    default: true,
  },
})
</script>

<style scoped>
h2 {
  text-align: center;
}

.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 90px;
  font-weight: 700;
}

.link-container {
  display: flex;
  justify-content: center;
}
</style>
