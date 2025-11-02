import { computed, type Ref } from "vue";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import type { TableName } from "@/types/api";

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

  return useRecordDetailsList(table, literatureIds);
}
