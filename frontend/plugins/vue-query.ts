import type {
  DehydratedState,
  VueQueryPluginOptions,
} from '@tanstack/vue-query'
import {
  VueQueryPlugin,
  QueryClient,
  hydrate,
  dehydrate,
} from '@tanstack/vue-query'
// Nuxt 3 app aliases
import { defineNuxtPlugin, useState } from '#imports'

export default defineNuxtPlugin((nuxt) => {
  const vueQueryState = useState<DehydratedState | null>('vue-query')

  // Modify your Vue Query global settings here
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        // Data is considered fresh for 5 minutes
        staleTime: 5 * 60 * 1000,
        // Cache data for 10 minutes
        gcTime: 10 * 60 * 1000, // Previously known as cacheTime
        // Retry failed requests 3 times (reduce retries on server)
        retry: import.meta.server ? 1 : 3,
        // Retry with exponential backoff
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        // Only refetch on window focus in production and on client
        refetchOnWindowFocus: !import.meta.server && process.env.NODE_ENV === 'production',
        // Don't refetch on reconnect by default to avoid unnecessary requests
        refetchOnReconnect: false,
        // Disable background refetching on server
        refetchOnMount: import.meta.server ? false : true,
        refetchInterval: false,
      },
      mutations: {
        // Retry failed mutations once
        retry: import.meta.server ? 0 : 1,
      },
    },
    
  })

  const options: VueQueryPluginOptions = { queryClient, enableDevtoolsV6Plugin: true, }

  nuxt.vueApp.use(VueQueryPlugin, options)

  if (import.meta.server) {
    nuxt.hooks.hook('app:rendered', () => {
      vueQueryState.value = dehydrate(queryClient)
    })
  }

  if (import.meta.client) {
    hydrate(queryClient, vueQueryState.value)
  }
})