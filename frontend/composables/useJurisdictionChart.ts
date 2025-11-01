import { useQuery } from "@tanstack/vue-query";
const fetchJurisdictionChartData = async () => {
  const response = await fetch("count_jurisdictions.json");
  const data = await response.json();

  const xValues = data.map((item: Record<string, unknown>) => item.n);
  const yValues = data.map(
    (item: Record<string, unknown>) => item.jurisdiction,
  );
  const links = data.map((item: Record<string, unknown>) => item.url);

  return {
    xValues,
    yValues,
    links,
  };
};

export function useJurisdictionChart() {
  return useQuery({
    queryKey: ["jurisdictionChart"],
    queryFn: fetchJurisdictionChartData,
  });
}
