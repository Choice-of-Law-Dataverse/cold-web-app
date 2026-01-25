import { ref, onMounted, onUnmounted } from "vue";

const isScrolled = ref(false);
const navHeight = ref(112); // 7rem default on desktop

function handleScroll() {
  isScrolled.value = window.scrollY > 20;
  // Update nav height based on scroll state
  navHeight.value = isScrolled.value ? 64 : 112; // 4rem vs 7rem on desktop
}

let listenerCount = 0;

export function useScrollState() {
  onMounted(() => {
    if (listenerCount === 0) {
      window.addEventListener("scroll", handleScroll, { passive: true });
      handleScroll();
    }
    listenerCount++;
  });

  onUnmounted(() => {
    listenerCount--;
    if (listenerCount === 0) {
      window.removeEventListener("scroll", handleScroll);
    }
  });

  return {
    isScrolled,
    navHeight,
  };
}
