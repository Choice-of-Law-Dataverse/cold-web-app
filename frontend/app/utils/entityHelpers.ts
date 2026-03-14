export function joinArbitralInstitutions(
  relations: { institution?: string | null }[],
): string | undefined {
  return (
    relations
      .map((inst) => inst.institution)
      .filter((v): v is string => Boolean(v && String(v).trim()))
      .join(", ") || undefined
  );
}
