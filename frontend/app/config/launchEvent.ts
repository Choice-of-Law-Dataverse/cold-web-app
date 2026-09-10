export const LAUNCH_EVENT_PATH = "/event/launch";

export const LAUNCH_EVENT_DATE = "28 April 2026";

export interface LaunchEventRecording {
  videoId: string;
  title: string;
}

export const LAUNCH_EVENT_RECORDINGS = {
  overview: {
    videoId: "wuInDfduDrU",
    title: "Understanding the Choice of Law Dataverse",
  },
  partyAutonomy: {
    videoId: "8-pMQGflqCc",
    title: "Party Autonomy: Sacred Principle or Legal Fiction?",
  },
  hcchPrinciples: {
    videoId: "DZwif-xDd-M",
    title: "Permanent Bureau Remarks on Ten Years of the HCCH Principles",
  },
  assessment: {
    videoId: "hxMn9UXxraM",
    title: "From Promise to Practice: CoLD Assessment",
  },
  pilResearchPartOne: {
    videoId: "SyijtyskG3Y",
    title: "Using the Dataverse for Advancing PIL Research (part 1)",
  },
  pilResearchPartTwo: {
    videoId: "lGA-nLXZAuY",
    title: "Using the Dataverse for Advancing PIL Research (part 2)",
  },
} as const satisfies Record<string, LaunchEventRecording>;

export const LAUNCH_EVENT_RECORDING_COUNT = Object.keys(
  LAUNCH_EVENT_RECORDINGS,
).length;

export function youTubeThumbnailUrl(videoId: string): string {
  return `https://i.ytimg.com/vi_webp/${videoId}/hq720.webp`;
}
