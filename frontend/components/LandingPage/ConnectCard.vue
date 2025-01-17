<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">CoLD Newsletter</h2>
    <div class="icon-container">
      <Icon name="i-bi:substack" size="96" style="color: #ff6719" />
    </div>
    <div class="link-container">
      <UButton
        class="suggestion-button"
        variant="link"
        icon="i-material-symbols:arrow-forward"
        trailing
      >
        Subscribe on Substack
      </UButton>
    </div>
  </UCard>
</template>

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
