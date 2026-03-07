import { AUTH0_ROLES_CLAIM, MODERATOR_ROLES } from "@/config/auth";

export default defineNuxtRouteMiddleware(async (to) => {
  const session = useUser();

  if (!session.value) {
    return navigateTo(
      `/auth/login?returnTo=${encodeURIComponent(to.fullPath)}`,
      { external: true },
    );
  }

  const roles = session.value[AUTH0_ROLES_CLAIM] || [];

  const hasRequiredRole =
    Array.isArray(roles) &&
    roles.some((role) =>
      MODERATOR_ROLES.includes(
        role.toLowerCase() as (typeof MODERATOR_ROLES)[number],
      ),
    );

  if (!hasRequiredRole) {
    throw createError({
      statusCode: 403,
      statusMessage: "Access Denied",
      message: "You do not have permission to access this page.",
    });
  }
});
