import { defineNuxtPlugin } from "#imports";
import { initNavigationDirection } from "@/composables/useNavigationDirection";

export default defineNuxtPlugin(() => {
  initNavigationDirection();
});
