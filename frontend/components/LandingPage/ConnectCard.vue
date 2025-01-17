<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="icon-container">
      <a
        :href="buttonLink"
        :target="newTab ? '_blank' : '_self'"
        :rel="newTab ? 'noopener noreferrer' : ''"
      >
        <!-- <Icon :name="iconName" size="96" style="color: #ff6719" /> -->
        <!-- <Icon name="i-bi:substack" size="96" :style="iconStyle" /> -->
        <Icon :name="iconName" size="96" :style="iconStyle" />
      </a>
    </div>
    <div class="link-container">
      <a
        :href="buttonLink"
        :target="newTab ? '_blank' : '_self'"
        :rel="newTab ? 'noopener noreferrer' : ''"
      >
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
// Define props
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
  iconStyle: {
    type: Object,
    default: () => ({
      color: '#ff6719', // Default color
    }),
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
