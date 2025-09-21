import { type Ref } from "vue";
import { useFullTable } from "@/composables/useFullTable";

export function useSpecialists(jurisdictionName: Ref<string>) {
  return useFullTable("Specialists", {
    filters: [{ column: "Jurisdiction", value: jurisdictionName.value }],
  });
}
