import { computed, type Ref } from "vue";
import { formatDate } from "@/utils/format.js";
import { useRecordDetails } from "@/composables/useRecordDetails";

function extractPdfUrl(pdfField: unknown): string | null {
  if (!pdfField || typeof pdfField !== "string") return null;
  
  try {
    // The PDF field is a string representation of a Python dict
    // Example: "{'id': '...', 'url': '...', 'filename': '...', ...}"
    // We need to parse it carefully
    const jsonStr = pdfField.replace(/'/g, '"'); // Replace single quotes with double quotes
    const pdfData = JSON.parse(jsonStr);
    return pdfData.url || null;
  } catch (e) {
    // If parsing fails, return null
    console.error("Failed to parse PDF field:", e);
    return null;
  }
}

export function useCourtDecision(courtDecisionId: Ref<string | number>) {
  return useRecordDetails(
    computed(() => "Court Decisions"),
    courtDecisionId,
    {
      select: (data) => {
        const pdfUrl = extractPdfUrl(data["Official Source (PDF)"]);
        return {
          ...data,
          "Case Title":
            data["Case Title"] === "Not found"
              ? data["Case Citation"]
              : data["Case Title"],
          "Related Literature": data["Themes"] || "",
          themes: data["Themes"] || "",
          "Case Citation": data["Case Citation"],
          Questions: data["Questions"],
          "Related Questions": data["Questions"],
          "Jurisdictions Alpha-3 Code": data["Jurisdictions Alpha-3 Code"],
          "Publication Date ISO": formatDate(
            data["Publication Date ISO"] as string,
          ),
          "Date of Judgment": formatDate(data["Date of Judgment"] as string),
          hasEnglishQuoteTranslation:
            data["Translated Excerpt"] &&
            (data["Translated Excerpt"] as string).trim() !== "",
          pdfUrl, // Add the extracted PDF URL
        };
      },
    },
  );
}
