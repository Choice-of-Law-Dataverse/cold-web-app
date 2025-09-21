# Centralized Error Handling

The application now features a centralized error handling system that leverages TanStack Vue Query and @nuxt/ui toast notifications to provide a consistent and user-friendly error experience.

## Key Components

### 1. `useErrorHandler` Composable

The main composable that provides centralized error handling functionality:

```typescript
import { useErrorHandler } from '@/composables/useErrorHandler'

const { handleError, handleNotFound, createQueryErrorHandler } = useErrorHandler()
```

#### Methods

- **`handleError(error, fallbackMessage?, options?)`**: Handle any type of error
- **`handleNotFound(resourceType, redirect?)`**: Handle specific "not found" errors
- **`createQueryErrorHandler(resourceType?, options?)`**: Create error handler for TanStack Query

### 2. Enhanced `useRecordDetails`

The composable now supports automatic error handling:

```typescript
// Basic usage with automatic error handling
const { data, isLoading, error } = useRecordDetails(table, id, {
  enableErrorHandling: true,     // Enable automatic error handling
  redirectOnNotFound: true,      // Redirect to /error for NotFoundError
  showToast: true,              // Show toast notifications for other errors
})
```

### 3. Enhanced Data Fetching Composables

All data fetching composables (like `useAnswer`) now support error handling options:

```typescript
const { data, isLoading, error } = useAnswer(answerId, {
  enableErrorHandling: true,
  redirectOnNotFound: true,
  showToast: true,
})
```

## Migration Guide

### Before (Old Pattern)

```vue
<script setup>
const { data, isLoading, error } = useRecordDetails(table, id)

// Manual error handling - 15-20 lines of boilerplate
watch(error, (newError) => {
  if (newError?.isNotFound) {
    router.push({
      path: '/error',
      query: { message: 'Resource not found' },
    })
  } else if (newError) {
    console.error('Error fetching resource:', newError)
  }
}, { immediate: true })

watch(data, (newData) => {
  if (newData && Object.keys(newData).length === 0) {
    router.push({
      path: '/error',
      query: { message: 'Resource not found' },
    })
  }
}, { immediate: true })
</script>
```

### After (New Pattern)

```vue
<script setup>
// Automatic error handling - 3 lines
const { data, isLoading, error } = useRecordDetails(table, id, {
  enableErrorHandling: true,
  redirectOnNotFound: true,
  showToast: true,
})

// Handle empty data as not found (if needed)
const { handleNotFound } = useErrorHandler()
watch(data, (newData) => {
  if (newData && Object.keys(newData).length === 0) {
    handleNotFound('Resource')
  }
}, { immediate: true })
</script>
```

## Error Types and Handling

### 1. NotFoundError
- **Default Behavior**: Redirects to `/error` page with appropriate message
- **Alternative**: Show toast notification if `redirectOnNotFound: false`

### 2. ApiError
- **Default Behavior**: Shows toast notification with error message
- **Fallback**: Console error logging

### 3. Generic Errors
- **Default Behavior**: Shows toast notification with fallback message
- **Fallback**: Console error logging

## Configuration Options

### Global Configuration

TanStack Query is configured with global error handling in `plugins/vue-query.ts`:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      onError: globalErrorHandler, // Handles unhandled errors
    },
    mutations: {
      onError: globalErrorHandler,
    },
  },
})
```

### Per-Query Configuration

Each query can override global behavior:

```typescript
const { data } = useRecordDetails(table, id, {
  enableErrorHandling: false,    // Disable automatic handling
  redirectOnNotFound: false,     // Show toast instead of redirect
  showToast: false,             // Don't show any notifications
})
```

## Toast Notifications

The system uses @nuxt/ui's toast system for non-critical errors:

- **Error Messages**: Red toast with error icon
- **Duration**: 5 seconds
- **Position**: Configurable via Nuxt UI settings
- **Actions**: Dismissible by user

## Best Practices

1. **Use Automatic Handling**: Enable for most pages to reduce boilerplate
2. **Custom Messages**: Provide meaningful fallback messages for better UX
3. **Selective Overrides**: Only disable automatic handling when you need custom behavior
4. **Toast vs Redirect**: Use toasts for recoverable errors, redirects for critical failures
5. **Error Logging**: All errors are automatically logged for debugging

## Examples

### Simple Page with Auto-handling
```vue
<script setup>
const { data, isLoading } = useRecordDetails(
  ref('Literature'), 
  ref(route.params.id),
  { enableErrorHandling: true }
)
</script>
```

### Custom Error Handling
```vue
<script setup>
const { handleError } = useErrorHandler()

const { data, isLoading } = useRecordDetails(
  ref('Literature'), 
  ref(route.params.id),
  { enableErrorHandling: false }
)

// Custom error handling logic
watchEffect(() => {
  if (error.value) {
    handleError(error.value, 'Failed to load literature', {
      showToast: true,
      redirectOnNotFound: false,
    })
  }
})
</script>
```

This centralized approach reduces code duplication, improves consistency, and provides a better user experience across the application.