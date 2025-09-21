import { useRouter } from 'vue-router'
import { useToast } from '#imports'
import { ApiError, NotFoundError } from '~/types/errors'

/**
 * Centralized error handling composable that provides:
 * 1. Consistent error handling across the application
 * 2. User-friendly error messages
 * 3. Automatic routing for critical errors
 * 4. Toast notifications for recoverable errors
 */
export function useErrorHandler() {
  const router = useRouter()
  const toast = useToast()

  /**
   * Handle errors based on their type and severity
   * @param error The error to handle
   * @param fallbackMessage Optional fallback message if error message is unclear
   * @param options Additional options for error handling
   */
  const handleError = (
    error: unknown,
    fallbackMessage?: string,
    options: {
      redirectOnNotFound?: boolean
      showToast?: boolean
      logError?: boolean
    } = {}
  ) => {
    const {
      redirectOnNotFound = true,
      showToast = true,
      logError = true,
    } = options

    if (logError) {
      console.error('Error occurred:', error)
    }

    // Handle NotFoundError
    if (error instanceof NotFoundError) {
      const errorMessage = error.table
        ? `${error.table} not found`
        : fallbackMessage || 'Resource not found'

      if (redirectOnNotFound) {
        router.push({
          path: '/error',
          query: { message: errorMessage },
        })
        return
      }

      if (showToast) {
        toast.add({
          title: 'Not Found',
          description: errorMessage,
          color: 'red',
          timeout: 5000,
        })
      }
      return
    }

    // Handle ApiError
    if (error instanceof ApiError) {
      const errorMessage = error.message || fallbackMessage || 'An error occurred'

      if (showToast) {
        toast.add({
          title: 'Error',
          description: errorMessage,
          color: 'red',
          timeout: 5000,
        })
      }
      return
    }

    // Handle generic errors
    const errorMessage =
      error instanceof Error
        ? error.message
        : fallbackMessage || 'An unexpected error occurred'

    if (showToast) {
      toast.add({
        title: 'Error',
        description: errorMessage,
        color: 'red',
        timeout: 5000,
      })
    }
  }

  /**
   * Handle not found errors specifically
   * @param resourceType The type of resource that was not found
   * @param redirect Whether to redirect to error page (default: true)
   */
  const handleNotFound = (resourceType: string, redirect: boolean = true) => {
    const errorMessage = `${resourceType} not found`

    if (redirect) {
      router.push({
        path: '/error',
        query: { message: errorMessage },
      })
      return
    }

    toast.add({
      title: 'Not Found',
      description: errorMessage,
      color: 'red',
      timeout: 5000,
    })
  }

  /**
   * TanStack Query error handler factory
   * Creates an error handler function optimized for TanStack Query
   * @param resourceType The type of resource being fetched
   * @param options Error handling options
   */
  const createQueryErrorHandler = (
    resourceType?: string,
    options: {
      redirectOnNotFound?: boolean
      showToast?: boolean
    } = {}
  ) => {
    return (error: unknown) => {
      // Check if this is a specific "not found" error
      if (error instanceof NotFoundError) {
        const message = resourceType || error.table || 'Resource'
        handleNotFound(message, options.redirectOnNotFound)
        return
      }

      // Handle other errors with toast notifications by default
      handleError(error, undefined, {
        redirectOnNotFound: false,
        showToast: options.showToast !== false,
        logError: true,
      })
    }
  }

  return {
    handleError,
    handleNotFound,
    createQueryErrorHandler,
  }
}