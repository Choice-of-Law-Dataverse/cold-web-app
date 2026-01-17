import { ref, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest, TableName } from "@/types/api";
import type { LiteratureResponse } from "@/types/entities/literature";
import { formatYear } from "@/utils/format";

async function fetchFullTableData<T>(
  table: TableName,
  filters: FullTableRequest["filters"] = [],
): Promise<T[]> {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = { table, filters };

  return await apiClient("/search/full_table", { body });
}

type Options<T> =
  | Partial<{
      select: (data: T[]) => T[];
      filters: FullTableRequest["filters"];
    }>
  | undefined;

export function useFullTable<T = Record<string, unknown>>(
  table: TableName,
  { select, filters }: Options<T> = {},
) {
  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
    ],
    queryFn: () => fetchFullTableData<T>(table, filters),
    select,
  });
}

// Entity-specific composables

export function useQuestions() {
  return useFullTable("Questions");
}

export function useInternationalLegalProvisions() {
  return useFullTable("International Legal Provisions", {
    select: (data) => {
      return data
        .slice()
        .sort((a: Record<string, unknown>, b: Record<string, unknown>) => {
          const aOrder =
            typeof a["Interface Order"] === "number"
              ? a["Interface Order"]
              : Number(a["Interface Order"]) || 0;
          const bOrder =
            typeof b["Interface Order"] === "number"
              ? b["Interface Order"]
              : Number(b["Interface Order"]) || 0;
          return aOrder - bOrder;
        });
    },
  });
}

export function useLeadingCases() {
  return useFullTable("Court Decisions", {
    select: (data) => {
      return data
        .filter((entry: Record<string, unknown>) => entry["Case Rank"] === 10)
        .sort(
          (a: Record<string, unknown>, b: Record<string, unknown>) =>
            Number(formatYear(b["Publication Date ISO"] as string)) -
            Number(formatYear(a["Publication Date ISO"] as string)),
        );
    },
    filters: [{ column: "Case Rank", value: 10 }],
  });
}

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  if (!jurisdiction.value) {
    return { data: ref<LiteratureResponse[]>([]), isLoading: ref(false) };
  }

  return useFullTable<LiteratureResponse>("Literature", {
    filters: [
      {
        column: "Jurisdiction",
        value: jurisdiction.value,
      },
    ],
  });
}
