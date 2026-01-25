export default defineNuxtRouteMiddleware((to) => {
  const session = useUser();

  if (!session.value) {
    return navigateTo(`/auth/login?returnTo=${to.path}`, { external: true });
  }
});
