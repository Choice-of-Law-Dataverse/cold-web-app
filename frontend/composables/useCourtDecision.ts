import { computed, type Ref } from "vue";
import { formatDate } from "@/utils/format";
import { useRecordDetails } from "@/composables/useRecordDetails";
import type { CourtDecisionResponse } from "@/types/entities/court-decision";

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  return useRecordDetails<CourtDecisionResponse>(
    computed(() => "Court Decisions"),
    courtDecisionId,
    {
      select: (data): CourtDecisionResponse => {
        const themes = data.themes as string | undefined;
        const questions = data["Questions"] as string | undefined;
        return {
          ...data,
          "Case Title":
            data["Case Title"] === "Not found"
              ? data["Case Citation"]
              : data["Case Title"],
          "Related Literature": themes,
          themes,
          "Case Citation": data["Case Citation"],
          Questions: questions,
          "Related Questions": questions,
          "Jurisdictions Alpha-3 Code": data["Jurisdictions Alpha-3 Code"],
          "Publication Date ISO":
            formatDate(data["Publication Date ISO"] as string) ?? undefined,
          "Date of Judgment":
            formatDate(data["Date of Judgment"] as string) ?? undefined,
          hasEnglishQuoteTranslation: Boolean(
            data["Translated Excerpt"] &&
              (data["Translated Excerpt"] as string).trim() !== "",
          ),
        };
      },
    },
  );
}
