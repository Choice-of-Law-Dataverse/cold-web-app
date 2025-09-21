import { formatYear } from "@/utils/format";
import { useFullTable } from "@/composables/useFullTable";

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
