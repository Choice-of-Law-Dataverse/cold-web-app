import { ref } from 'vue'

export function useLegalState() {
  const loading = ref(false)
  const error = ref(null)

  const setLoading = (value) => {
    loading.value = value
    if (value) error.value = null
  }

  const setError = (message) => {
    error.value = message
    loading.value = false
  }

  const resetState = () => {
    loading.value = false
    error.value = null
  }

  return {
    loading,
    error,
    setLoading,
    setError,
    resetState,
  }
}
