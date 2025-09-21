<template>
  <div>
    <slot v-if="!error" />
    <div v-else-if="isNotFoundError" class="entity-not-found">
      <div class="bg-cold-bg min-h-screen flex flex-col">
        <!-- Navigation Bar -->
        <Nav />
        
        <!-- Main Content Area -->
        <main class="flex-1 mt-12 px-6">
          <div
            class="mx-auto min-h-[50vh] flex flex-col justify-center items-center text-center"
            style="max-width: var(--container-width); width: 100%"
          >
            <h2>{{ notFoundMessage }}</h2>
            
            <NuxtLink to="/" class="mt-6"> Take me back to Home </NuxtLink>
          </div>
        </main>
        
        <Footer />
      </div>
    </div>
    <div v-else class="entity-error">
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
import { ref, computed, onErrorCaptured, provide, inject } from 'vue'
import Nav from '@/components/layout/Nav.vue'
import Footer from '@/components/layout/Footer.vue'

const props = defineProps({
  onError: {
    type: Function,
    default: undefined
  },
  entityType: {
    type: String,
    default: 'Entity'
  }
})

const error = ref(null)

// Check if error is a NotFoundError
const isNotFoundError = computed(() => {
  return error.value?.statusCode === 404 || 
         error.value?.data?.name === 'NotFoundError' ||
         error.value?.name === 'NotFoundError'
})

// Generate not found message based on entity type
const notFoundMessage = computed(() => {
  if (error.value?.statusMessage) {
    return error.value.statusMessage
  }
  return `${props.entityType} not found`
})

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
  
  // For non-NotFound errors, show toast notification
  if (!isNotFoundError.value) {
    const toast = inject('toast', null)
    if (toast) {
      toast.add({
        title: 'Error',
        description: err.message || 'An unexpected error occurred',
        color: 'red',
        timeout: 5000
      })
    }
  }
  
  console.error('Error caught by EntityErrorBoundary:', err, info)
  
  // Prevent the error from bubbling up
  return false
})

// Provide retry function to child components
provide('errorBoundary', { retry })
</script>