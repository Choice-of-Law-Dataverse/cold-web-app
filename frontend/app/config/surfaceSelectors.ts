export const QUESTIONS_HASH = "#questions-and-answers";

export const SURFACE_TRANSITION_CLASS = "surface-transition";

export const DRAWER_PANEL_CLASS = "entity-drawer-panel";

export const SURFACE_DESTINATIONS = {
  search: "[data-search-surface][data-surface-ready]",
  detail: "[data-detail-surface][data-surface-ready]",
  list: '.entity-list-table:not([aria-busy="true"])',
  questions: QUESTIONS_HASH,
  drawer: `.${DRAWER_PANEL_CLASS}[data-state="open"]:has([data-drawer-ready])`,
} as const;
