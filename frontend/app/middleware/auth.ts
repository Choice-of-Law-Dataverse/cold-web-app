export default defineNuxtRouteMiddleware((to) => {
  const session = useUser();

  if (!session.value) {
    return navigateTo(
      `/auth/login?returnTo=${encodeURIComponent(to.fullPath)}`,
      { external: true },
    );
  }
});
