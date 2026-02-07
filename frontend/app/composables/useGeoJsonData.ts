import { useQuery } from "@tanstack/vue-query";
import type { FeatureCollection, Geometry } from "geojson";

interface GeoJsonProperties {
  iso_a3_eh: string;
  name: string;
}

type GeoJsonData = FeatureCollection<Geometry, GeoJsonProperties>;

const fetchGeoJsonData = async (): Promise<GeoJsonData> => {
  const response = await fetch("/geo.json");
  if (!response.ok) {
    throw new Error("Failed to fetch GeoJSON file");
  }
  return await response.json();
};

export function useGeoJsonData() {
  return useQuery({
    queryKey: ["geoJsonData"],
    queryFn: fetchGeoJsonData,
    // GeoJSON is static data - cache aggressively
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60 * 24, // 24 hours (garbage collection)
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
}
