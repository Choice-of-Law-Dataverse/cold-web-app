import { computed, ref } from "vue";

/**
 * Stand-in for Nuxt's virtual `#imports` module.
 *
 * Vitest runs outside the Nuxt build, so the virtual module does not exist.
 * Only the helpers unit-tested code actually reaches for are provided; add
 * more here rather than importing them implicitly.
 */

export interface NuxtErrorInput {
  statusCode?: number;
  statusMessage?: string;
  message?: string;
  fatal?: boolean;
}

export function createError(input: NuxtErrorInput | string): Error {
  if (typeof input === "string") return new Error(input);
  const error = new Error(input.statusMessage ?? input.message ?? "Error");
  Object.assign(error, input);
  return error;
}

export function useRuntimeConfig() {
  const globalConfig = (
    globalThis as { useRuntimeConfig?: () => Record<string, unknown> }
  ).useRuntimeConfig;
  return globalConfig ? globalConfig() : { public: {} };
}

export function useRoute() {
  return { path: "/", fullPath: "/", params: {}, query: {} };
}

export function useState<T>(_key: string, init?: () => T) {
  return ref(init ? init() : undefined);
}

export function useHead() {}

export function useSeoMeta() {}

export function useRobotsRule() {
  return ref(undefined);
}

export { computed };
