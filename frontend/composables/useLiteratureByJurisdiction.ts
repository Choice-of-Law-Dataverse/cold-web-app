import { useFullTable } from "@/composables/useFullTable";

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  if (!jurisdiction.value) {
    return { data: ref([]), isLoading: ref(false) };
  }

  return useFullTable("Literature", {
    filters: [
      {
        column: "Jurisdiction",
        value: jurisdiction.value,
      },
    ],
  });
}
