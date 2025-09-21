import { useQuery } from "@tanstack/vue-query";

const fetchGeoJsonData = async () => {
  const response = await fetch("/temp_custom.geo.json");
  if (!response.ok) {
    throw new Error("Failed to fetch GeoJSON file");
  }
  return await response.json();
};

export function useGeoJsonData() {
  return useQuery({
    queryKey: ["geoJsonData"],
    queryFn: fetchGeoJsonData,
  });
}
