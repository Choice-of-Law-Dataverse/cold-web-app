import { ref, onMounted, onUnmounted } from "vue";

const isModKeyHeld = ref(false);
let listenerCount = 0;

function handleKeyDown(e: KeyboardEvent) {
  if (e.metaKey || e.ctrlKey) {
    isModKeyHeld.value = true;
  }
}

function handleKeyUp(e: KeyboardEvent) {
  if (!e.metaKey && !e.ctrlKey) {
    isModKeyHeld.value = false;
  }
}

function handleBlur() {
  isModKeyHeld.value = false;
}

export function useModKeyState() {
  onMounted(() => {
    if (listenerCount === 0) {
      window.addEventListener("keydown", handleKeyDown);
      window.addEventListener("keyup", handleKeyUp);
      window.addEventListener("blur", handleBlur);
    }
    listenerCount++;
  });

  onUnmounted(() => {
    listenerCount--;
    if (listenerCount === 0) {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      window.removeEventListener("blur", handleBlur);
    }
  });

  return { isModKeyHeld };
}
