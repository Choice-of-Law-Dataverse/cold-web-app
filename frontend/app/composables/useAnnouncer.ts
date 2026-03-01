import { ref } from "vue";

const announcement = ref("");

export function useAnnouncer() {
  function announce(message: string) {
    announcement.value = "";
    requestAnimationFrame(() => {
      announcement.value = message;
    });
  }

  return { announcement, announce };
}
