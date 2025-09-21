import { defineNuxtPlugin } from '#app'
import { ref } from 'vue'

export default defineNuxtPlugin(() => {
  // Check if Nuxt UI's useToast is available
  let toast = null
  
  try {
    // Try to use Nuxt UI's toast if available
    if (typeof useToast !== 'undefined') {
      toast = useToast()
    }
  } catch (e) {
    // useToast not available, we'll create our own
  }
  
  // If toast is not available, create a simple notification system
  if (!toast) {
    const notifications = ref([])
    
    const add = (notification) => {
      const id = Date.now() + Math.random()
      const notif = { 
        id, 
        timeout: 5000, 
        ...notification 
      }
      
      notifications.value.push(notif)
      
      if (notif.timeout > 0) {
        setTimeout(() => {
          remove(id)
        }, notif.timeout)
      }
      
      return notif
    }
    
    const remove = (id) => {
      const index = notifications.value.findIndex(n => n.id === id)
      if (index > -1) {
        notifications.value.splice(index, 1)
      }
    }
    
    const clear = () => {
      notifications.value = []
    }
    
    toast = { add, remove, clear, notifications }
  }
  
  // Provide to the app
  return {
    provide: {
      toast
    }
  }
})