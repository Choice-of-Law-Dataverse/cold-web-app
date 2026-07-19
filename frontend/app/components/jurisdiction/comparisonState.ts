import type { InjectionKey, ComputedRef, Ref } from "vue";
import type { JurisdictionOption } from "@/types/analyzer";

export interface Row {
  id: string;
  question: string | null | undefined;
  answer?: string;
  answerLink?: string;
  answers?: Record<string, string>;
  matchStatus: "match" | "mismatch" | "na";
  level: number;
  theme: string;
}

export interface ComparisonState {
  jurisdictions: ComputedRef<JurisdictionOption[]>;
  answersMap: Ref<Map<string, Map<string, string>> | undefined>;
  removeJurisdiction: (coldId?: string) => void;
  answersLoading: Ref<boolean>;
  isScrollable: ComputedRef<boolean>;
  stickyColLeft: ComputedRef<string>;
  allJurisdictionsHaveAnswersLoaded: ComputedRef<boolean>;
  hasAnswersForJurisdiction: (coldId?: string) => boolean;
  shouldShowDash: (answer: string | undefined) => boolean;
  handleAnswerClick: (
    event: MouseEvent,
    coldId: string,
    questionId: string,
  ) => void;
  getAnswerLink: (coldId: string, questionId: string) => string;
  isBoldQuestion: (questionId: string) => boolean;
  jurisdictionLabel: (j: JurisdictionOption) => string;
}

export const ComparisonStateKey = Symbol(
  "ComparisonState",
) as InjectionKey<ComparisonState>;
