export type ModerationStatus =
  | "pending"
  | "draft"
  | "analyzing"
  | "completed"
  | "failed"
  | "approved"
  | "rejected";

export type BadgeColor =
  | "info"
  | "neutral"
  | "success"
  | "error"
  | "warning"
  | "primary"
  | "secondary";

export function getStatusBadgeColor(status?: string): BadgeColor {
  switch (status) {
    case "pending":
      return "info";
    case "draft":
      return "neutral";
    case "analyzing":
      return "primary";
    case "completed":
      return "success";
    case "failed":
      return "error";
    case "approved":
      return "success";
    case "rejected":
      return "error";
    default:
      return "neutral";
  }
}

/**
 * Get status label for moderation/admin views (shorter labels)
 */
export function getStatusLabel(status?: string): string {
  switch (status) {
    case "pending":
      return "Pending";
    case "draft":
      return "Draft";
    case "analyzing":
      return "Analyzing";
    case "completed":
      return "Completed";
    case "failed":
      return "Failed";
    case "approved":
      return "Approved";
    case "rejected":
      return "Rejected";
    default:
      return status || "Unknown";
  }
}

/**
 * Get status label for user-facing views (more descriptive labels)
 */
export function getStatusLabelForUser(status?: string): string {
  switch (status) {
    case "pending":
      return "Pending Review";
    case "draft":
      return "Draft";
    case "analyzing":
      return "Analyzing";
    case "completed":
      return "Ready to Submit";
    case "failed":
      return "Failed";
    case "approved":
      return "Approved";
    case "rejected":
      return "Rejected";
    default:
      return status || "Unknown";
  }
}

/**
 * Check if a case analysis can be recovered/resumed
 */
export function canRecoverAnalysis(status: string): boolean {
  return !["approved", "rejected", "pending"].includes(status);
}

/**
 * Get action text for user's analysis list
 */
export function getAnalysisActionText(status: string): string {
  switch (status) {
    case "pending":
      return "In Review";
    case "approved":
      return "Published";
    case "rejected":
      return "Rejected";
    default:
      return "";
  }
}
