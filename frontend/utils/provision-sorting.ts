/**
 * Utility functions for sorting legal provision IDs based on ranking data
 */

/**
 * Returns provision IDs sorted by their "Ranking (Display Order)" value.
 * The backend now supplies a field that can associate ordering with provisions.
 * Assumptions:
 *  - rankingData may contain a mapping object
 *    like "Ranking (Display Order)": "provA:1,provB:2" OR "1:provA,2:provB" OR JSON array/object.
 *  - If the ranking field is absent or unparsable, we fall back to the original order.
 */
export function getSortedProvisionIds(rawValue: string, rankingData?: unknown): string[] {
  if (!rawValue) return [];
  
  const ids = rawValue
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (!rankingData) return ids;

  // Try a few parsing strategies
  let rankingMap: Record<string, number> = {};
  
  try {
    if (typeof rankingData === "string") {
      // Strategy 0: Simple numeric CSV (e.g. "2,1,3") aligned by index to ids
      if (
        typeof rankingData === "string" &&
        /^(\s*\d+\s*)([,;]\s*\d+\s*)*$/.test(rankingData.trim())
      ) {
        const nums = rankingData.split(/[,;]+/).map((n) => Number(n.trim()));
        if (nums.length === ids.length) {
          ids.forEach((pid, idx) => {
            const r = nums[idx];
            if (!isNaN(r)) rankingMap[pid] = r;
          });
        }
      }

      // Try JSON first
      if (
        rankingData.trim().startsWith("{") ||
        rankingData.trim().startsWith("[")
      ) {
        const parsed = JSON.parse(rankingData);
        if (Array.isArray(parsed)) {
          // If array, assume it is in order already
          parsed.forEach((pid, idx) => {
            if (typeof pid === "string") rankingMap[pid] = idx + 1;
          });
        } else if (parsed && typeof parsed === "object") {
          rankingMap = Object.fromEntries(
            Object.entries(parsed).map(([k, v]) => {
              // Accept either key=provisionId, value=rank OR key=rank, value=provisionId
              if (ids.includes(k) && !isNaN(Number(v))) {
                return [k, Number(v)];
              }
              if (ids.includes(String(v)) && !isNaN(Number(k))) {
                return [String(v), Number(k)];
              }
              return [k, Number(v)]; // fallback
            }),
          );
        }
      } else {
        // Handle simple delimited patterns: "provA:1,provB:2" or "1:provA,2:provB"
        rankingData.split(/[,;]+/).forEach((pair) => {
          const [a, b] = pair.split(":").map((s) => s && s.trim());
          if (!a || !b) return;
          if (ids.includes(a) && !isNaN(Number(b))) {
            rankingMap[a] = Number(b);
          } else if (ids.includes(b) && !isNaN(Number(a))) {
            rankingMap[b] = Number(a);
          }
        });
      }
    } else if (Array.isArray(rankingData)) {
      rankingData.forEach((pid, idx) => {
        if (typeof pid === "string") rankingMap[pid] = idx + 1;
      });
    } else if (rankingData && typeof rankingData === "object") {
      rankingMap = Object.fromEntries(
        Object.entries(rankingData as Record<string, unknown>).map(([k, v]) => {
          if (ids.includes(k) && !isNaN(Number(v))) return [k, Number(v)];
          if (ids.includes(String(v)) && !isNaN(Number(k)))
            return [String(v), Number(k)];
          return [k, Number(v)];
        }),
      );
    }
  } catch (e) {
    console.warn("Failed to parse Ranking (Display Order):", e);
  }

  // If we got no usable ranking numbers, keep original order
  const hasNumbers = Object.values(rankingMap).some(
    (n) => typeof n === "number" && !isNaN(n),
  );
  if (!hasNumbers) return ids;

  return [...ids].sort((a, b) => {
    const ra = rankingMap[a];
    const rb = rankingMap[b];
    if (ra == null && rb == null) return 0;
    if (ra == null) return 1; // unranked go last
    if (rb == null) return -1;
    return ra - rb;
  });
}