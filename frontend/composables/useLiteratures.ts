import { computed, type Ref } from "vue";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import type { TableName } from "@/types/api";
import type { LiteratureResponse } from "@/types/entities/literature";

export function useLiteratures(ids: Ref<string>) {
  const literatureIds = computed(() =>
    ids.value
      ? ids.value
          .split(",")
          .map((id: string) => id.trim())
          .filter((id: string) => id)
      : [],
  );

  const table = computed<TableName>(() => "Literature");

  return useRecordDetailsList<LiteratureResponse>(table, literatureIds);
}
