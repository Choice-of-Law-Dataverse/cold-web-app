import { defineNuxtPlugin } from "#imports";

export default defineNuxtPlugin(async () => {
  const user = useUser();
  if (user.value) return;
  try {
    user.value = (await $fetch("/api/auth/me")) ?? undefined;
  } catch {
    user.value = undefined;
  }
});
