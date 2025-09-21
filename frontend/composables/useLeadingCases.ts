import { formatYear } from "@/utils/format";
import { useFullTable } from "@/composables/useFullTable";

export function useLeadingCases() {
  return useFullTable("Court Decisions", {
    select: (data) => {
      return data
        .filter((entry: any) => entry["Case Rank"] === 10)
        .sort(
          (a: any, b: any) =>
            Number(formatYear(b["Publication Date ISO"])) -
            Number(formatYear(a["Publication Date ISO"])),
        );
    },
    filters: [{ column: "Case Rank", value: 10 }],
  });
}
