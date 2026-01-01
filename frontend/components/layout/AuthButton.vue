<template>
  <div class="auth-button-container">
    <template v-if="user">
      <UButton
        variant="link"
        class="font-semibold !text-cold-night"
        @click="handleLogout"
      >
        Logout
      </UButton>
    </template>
    <template v-else>
      <UButton
        variant="link"
        class="font-semibold !text-cold-night"
        @click="handleLogin"
      >
        Login
      </UButton>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const user = ref(null);

onMounted(async () => {
  try {
    const { data } = await useFetch("/api/auth/session");
    if (data.value?.user) {
      user.value = data.value.user;
    }
  } catch {
    console.log("No user session");
  }
});

function handleLogin() {
  navigateTo("/auth/login", { external: true });
}

function handleLogout() {
  navigateTo("/auth/logout", { external: true });
}
</script>

<style scoped>
.auth-button-container {
  display: flex;
  align-items: center;
}
</style>
