import mitt from "mitt";

type EventMap = Record<string, unknown>;

const eventBus = mitt<EventMap>();

export type EventBus = typeof eventBus;
export default eventBus;
