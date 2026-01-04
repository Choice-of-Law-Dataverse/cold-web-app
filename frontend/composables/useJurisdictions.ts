import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { JurisdictionWithAnswerCoverage } from "@/types/api";

const EMPTY_SET = new Set<string>();

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

  const { data, ...rest } = useQuery({
    queryKey: ["jurisdictions-with-answer-percentage"],
    queryFn: () =>
      apiClient<JurisdictionWithAnswerCoverage[]>(
        "/statistics/jurisdictions-with-answer-percentage",
        { method: "GET" },
      ),
    select: (rawData) => {
      const jurisdictions = rawData
        .filter((record) => record["Irrelevant?"] === false)
        .map(convert);

      const knownJurisdictionTerms = new Set<string>();
      jurisdictions.forEach((j) => {
        knownJurisdictionTerms.add(j.Name.toLowerCase());
        if (j.alpha3Code) {
          knownJurisdictionTerms.add(j.alpha3Code.toLowerCase());
        }
      });

      return {
        jurisdictions,
        knownJurisdictionTerms,
      };
    },
  });

  return {
    data: computed(() => data.value?.jurisdictions),
    knownJurisdictionTerms: computed(
      () => data.value?.knownJurisdictionTerms ?? EMPTY_SET,
    ),
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
