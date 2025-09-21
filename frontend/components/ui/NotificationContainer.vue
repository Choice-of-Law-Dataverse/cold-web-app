<template>
  <div
    v-if="notifications && notifications.length > 0"
    class="fixed top-4 right-4 z-50 space-y-3"
  >
    <transition-group
      name="notification"
      tag="div"
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="transform translate-x-full opacity-0"
      enter-to-class="transform translate-x-0 opacity-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="transform translate-x-0 opacity-100"
      leave-to-class="transform translate-x-full opacity-0"
    >
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="max-w-sm w-full bg-white border border-gray-200 rounded-lg shadow-lg p-4"
        :class="{
          'border-red-200 bg-red-50': notification.color === 'red',
          'border-green-200 bg-green-50': notification.color === 'green',
          'border-yellow-200 bg-yellow-50': notification.color === 'yellow',
          'border-blue-200 bg-blue-50': notification.color === 'blue',
        }"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <Icon
              v-if="notification.color === 'red'"
              name="i-material-symbols:error-outline"
              class="w-5 h-5 text-red-500"
            />
            <Icon
              v-else-if="notification.color === 'green'"
              name="i-material-symbols:check-circle-outline"
              class="w-5 h-5 text-green-500"
            />
            <Icon
              v-else-if="notification.color === 'yellow'"
              name="i-material-symbols:warning-outline"
              class="w-5 h-5 text-yellow-500"
            />
            <Icon
              v-else
              name="i-material-symbols:info-outline"
              class="w-5 h-5 text-blue-500"
            />
          </div>
          <div class="ml-3 flex-1">
            <h4
              v-if="notification.title"
              class="text-sm font-medium"
              :class="{
                'text-red-800': notification.color === 'red',
                'text-green-800': notification.color === 'green',
                'text-yellow-800': notification.color === 'yellow',
                'text-blue-800': notification.color === 'blue',
                'text-gray-800': !notification.color
              }"
            >
              {{ notification.title }}
            </h4>
            <p
              v-if="notification.description"
              class="text-sm mt-1"
              :class="{
                'text-red-700': notification.color === 'red',
                'text-green-700': notification.color === 'green',
                'text-yellow-700': notification.color === 'yellow',
                'text-blue-700': notification.color === 'blue',
                'text-gray-600': !notification.color
              }"
            >
              {{ notification.description }}
            </p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              @click="$emit('remove', notification.id)"
              class="rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Icon name="i-material-symbols:close" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
defineProps({
  notifications: {
    type: Array,
    default: () => []
  }
})

defineEmits(['remove'])
</script>