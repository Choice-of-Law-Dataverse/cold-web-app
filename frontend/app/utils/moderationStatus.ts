export type ModerationStatus =
  | "pending"
  | "draft"
  | "analyzing"
  | "completed"
  | "failed"
  | "approved"
  | "rejected"
  | "reviewed"
  | "dismissed";

export type BadgeColor =
  | "info"
  | "neutral"
  | "success"
  | "error"
  | "warning"
  | "primary"
  | "secondary";

export function getStatusBadgeColor(status?: string | null): BadgeColor {
  switch (status as ModerationStatus) {
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
    case "reviewed":
      return "success";
    case "dismissed":
      return "neutral";
    default:
      return "neutral";
  }
}

export function getStatusLabel(status?: string | null): string {
  switch (status as ModerationStatus) {
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
    case "reviewed":
      return "Reviewed";
    case "dismissed":
      return "Dismissed";
    default:
      return status || "Unknown";
  }
}

export function getStatusLabelForUser(status?: string | null): string {
  switch (status as ModerationStatus) {
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

export function canRecoverAnalysis(status: string): boolean {
  return !["approved", "rejected", "pending"].includes(status);
}

export function getAnalysisActionText(status: string): string {
  switch (status as ModerationStatus) {
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
