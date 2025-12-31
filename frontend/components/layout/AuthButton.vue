<template>
  <div class="auth-button-container">
    <template v-if="user">
      <UButton
        variant="link"
        class="!text-cold-night font-semibold"
        @click="handleLogout"
      >
        Logout
      </UButton>
    </template>
    <template v-else>
      <UButton
        variant="link"
        class="!text-cold-night font-semibold"
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
  // Check if Auth0 is available and user is logged in
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
  // Redirect to Auth0 login
  window.location.href = "/api/auth/login";
}

function handleLogout() {
  // Redirect to Auth0 logout
  window.location.href = "/api/auth/logout";
}
</script>

<style scoped>
.auth-button-container {
  display: flex;
  align-items: center;
}
</style>
