import createClient from "openapi-fetch";
import type { paths } from "@/types/api-schema";

export function useApiClient() {
  const config = useRuntimeConfig();

  const baseUrl =
    typeof window === "undefined"
      ? `${config.public.siteUrl}/api/proxy`
      : "/api/proxy";

  const client = createClient<paths>({
    baseUrl,
    headers: { "Content-Type": "application/json" },
  });

  return { client };
}
