import type { Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";

export interface Specialist {
  id: number;
  created_at: string | null;
  updated_at: string | null;
  created_by: string | null;
  updated_by: string | null;
  nc_order: number | null;
  ncRecordId: string | null;
  ncRecordHash: string | null;
  Specialist: string | null;
  Created: string | null;
}

async function fetchSpecialists(jurisdictionAlphaCode: string): Promise<Specialist[]> {
  const { apiClient } = useApiClient();
  return await apiClient<Specialist[]>(`/search/specialists/${encodeURIComponent(jurisdictionAlphaCode)}`, {
    method: "GET",
  });
}

export function useSpecialists(jurisdictionAlphaCode: Ref<string>) {
  return useQuery({
    queryKey: ["specialists", jurisdictionAlphaCode],
    queryFn: () => fetchSpecialists(jurisdictionAlphaCode.value),
    enabled: () => !!jurisdictionAlphaCode.value,
  });
}
