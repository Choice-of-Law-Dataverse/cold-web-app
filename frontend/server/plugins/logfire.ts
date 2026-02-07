import * as logfire from "@pydantic/logfire-node";

export default defineNitroPlugin(() => {
  const config = useRuntimeConfig();

  if (config.logfire?.token) {
    try {
      logfire.configure({
        token: config.logfire.token,
        serviceName: config.logfire.serviceName || "cold-frontend",
        serviceVersion: config.logfire.serviceVersion || "1.0.0",
      });

      console.log("[Logfire] Configured successfully");
    } catch (error) {
      console.error("[Logfire] Configuration failed:", error);
    }
  } else {
    console.log("[Logfire] Skipped - no token provided");
  }
});
