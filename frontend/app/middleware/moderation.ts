export default defineNuxtRouteMiddleware(async (to) => {
  const session = useUser();

  // Check if user is logged in
  if (!session.value) {
    return navigateTo(
      `/auth/login?returnTo=${encodeURIComponent(to.fullPath)}`,
      { external: true },
    );
  }

  const roles = session.value["https://cold.global/roles"] || [];

  const hasRequiredRole =
    Array.isArray(roles) &&
    roles.some(
      (role) =>
        role.toLowerCase() === "editor" || role.toLowerCase() === "admin",
    );

  if (!hasRequiredRole) {
    // User is logged in but doesn't have the required role
    throw createError({
      statusCode: 403,
      statusMessage: "Access Denied",
      message: "You do not have permission to access this page.",
    });
  }
});
