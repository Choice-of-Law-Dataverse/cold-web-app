import type { components } from "@/types/api-schema";

export type SpecialistResponse = components["schemas"]["SpecialistRecord"];
export type SpecialistDetailResponse =
  components["schemas"]["SpecialistDetail"];

export type Specialist = SpecialistDetailResponse;

export function processSpecialist(raw: SpecialistDetailResponse): Specialist {
  return raw;
}
