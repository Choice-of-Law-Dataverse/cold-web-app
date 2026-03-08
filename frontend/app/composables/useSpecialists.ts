import type { Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { components } from "@/types/api-schema";

export type Specialist = components["schemas"]["SpecialistResponse"];

async function fetchSpecialists(
  jurisdictionAlphaCode: string,
): Promise<Specialist[]> {
  const { client } = useApiClient();
  const { data, error } = await client.GET(
    "/search/specialists/{jurisdiction_alpha_code}",
    {
      params: {
        path: { jurisdiction_alpha_code: jurisdictionAlphaCode },
      },
    },
  );
  if (error || !data) throw error ?? new Error("No data returned");
  return data;
}

export function useSpecialists(jurisdictionAlphaCode: Ref<string>) {
  return useQuery({
    queryKey: ["specialists", jurisdictionAlphaCode],
    queryFn: () => fetchSpecialists(jurisdictionAlphaCode.value),
    enabled: () => !!jurisdictionAlphaCode.value,
  });
}
