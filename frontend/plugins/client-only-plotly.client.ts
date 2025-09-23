export default defineNuxtPlugin(() => {
  // Only register on client side
  if (!import.meta.server) {
    // This will ensure plotly components are only loaded on the client
  }
})