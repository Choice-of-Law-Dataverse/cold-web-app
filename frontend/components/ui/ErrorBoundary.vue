<template>
  <div>
    <slot v-if="!error" />
    <div v-else class="error-boundary">
      <slot name="fallback" :error="error" :retry="retry">
        <div class="flex flex-col items-center justify-center min-h-64 p-8 text-center">
          <div class="mb-4">
            <Icon name="i-material-symbols:error-outline" class="w-12 h-12 text-red-500" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Something went wrong
          </h3>
          <p class="text-gray-600 mb-4">
            {{ error.message || 'An unexpected error occurred' }}
          </p>
          <UButton @click="retry" color="primary" variant="outline">
            Try Again
          </UButton>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured, provide, inject } from 'vue'

const props = defineProps({
  onError: {
    type: Function,
    default: undefined
  }
})

const error = ref(null)

// Error recovery function
const retry = () => {
  error.value = null
}

// Capture errors from child components
onErrorCaptured((err, instance, info) => {
  error.value = err
  
  // Call custom error handler if provided
  if (props.onError) {
    props.onError(err, instance, info)
  }
  
  // Show toast notification
  const toast = inject('toast', null)
  if (toast) {
    toast.add({
      title: 'Error',
      description: err.message || 'An unexpected error occurred',
      color: 'red',
      timeout: 5000
    })
  }
  
  console.error('Error caught by ErrorBoundary:', err, info)
  
  // Prevent the error from bubbling up
  return false
})

// Provide retry function to child components
provide('errorBoundary', { retry })
</script>