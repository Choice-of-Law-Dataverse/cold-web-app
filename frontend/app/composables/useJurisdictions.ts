import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { JurisdictionWithAnswerCoverage } from "@/types/api";

function convert(record: JurisdictionWithAnswerCoverage) {
  return {
    ...record,
    Name: record?.Name || "N/A",
    "Jurisdiction Summary": record?.["Jurisdiction Summary"] || "N/A",
    "Jurisdictional Differentiator":
      record?.["Jurisdictional Differentiator"] || "N/A",
    "Legal Family": record?.["Legal Family"] || "N/A",
    Specialists: record?.Specialists || "",
    Literature: record?.Literature,
    label: record.Name as string,
    alpha3Code: record["Alpha-3 Code"] as string | undefined,
    avatar: record["Alpha-3 Code"]
      ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${String(
          record["Alpha-3 Code"],
        ).toLowerCase()}.svg`
      : undefined,
    answerCoverage: record["Answer Coverage"],
  };
}

export function useJurisdictions() {
  const { apiClient } = useApiClient();

  const { data: rawData, ...rest } = useQuery({
    queryKey: ["jurisdictions-with-answer-percentage"],
    queryFn: () =>
      apiClient<JurisdictionWithAnswerCoverage[]>(
        "/statistics/jurisdictions-with-answer-percentage",
        { method: "GET" },
      ),
  });

  const data = computed(() => {
    if (!rawData.value) return undefined;

    return rawData.value
      .filter(
        (record: JurisdictionWithAnswerCoverage) =>
          record["Irrelevant?"] === false,
      )
      .map(convert);
  });

  return {
    data,
    ...rest,
  };
}

export function useJurisdiction(iso3: Ref<string>) {
  const { data: jurisdictionsData, ...rest } = useJurisdictions();

  const data = computed(() => {
    const isoValue = iso3.value;
    const records = jurisdictionsData.value;

    if (!isoValue || !records) {
      return undefined;
    }

    const iso3Code = isoValue.toLocaleUpperCase();

    const match = records.find(
      (r) => r.alpha3Code?.toLocaleUpperCase() === iso3Code,
    );

    return match;
  });

  return {
    data,
    ...rest,
  };
}
