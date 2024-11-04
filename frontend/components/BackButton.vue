<template>
  <div style="margin-bottom: 48px">
    <UButton
      @click="goBack"
      variant="link"
      icon="i-material-symbols:arrow-back"
      :trailing="false"
      class="suggestion-button"
    >
      Back to Results
    </UButton>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.back() // Takes the user to the previous page
}
</script>
