import type { Ref } from "vue";
import { computed, isRef } from "vue";

interface EmptyValueBehavior {
  action: string;
  fallback?: string;
  fallbackClass?: string;
  getFallback?: (data: Record<string, unknown>) => string;
  shouldDisplay?: (data: Record<string, unknown>) => boolean;
}

interface KeyLabelPair {
  key: string;
  label: string;
  emptyValueBehavior?: EmptyValueBehavior;
}

export interface CardConfig {
  keyLabelPairs: KeyLabelPair[];
  valueClassMap: Record<string, string>;
  processData?: (
    data: Record<string, unknown>,
  ) => Record<string, unknown> | null;
  [key: string]: unknown;
}

type ResultData = Record<string, unknown> | Ref<Record<string, unknown> | null>;

function unwrap(data: ResultData): Record<string, unknown> | null {
  if (isRef(data)) {
    return (data as Ref<Record<string, unknown> | null>).value;
  }
  return data as Record<string, unknown>;
}

export function useCardFields(config: CardConfig, resultData: ResultData) {
  const processedData = computed(() => {
    const raw = unwrap(resultData);
    if (!raw) return null;
    return config.processData ? config.processData(raw) : raw;
  });

  function findPair(key: string): KeyLabelPair | undefined {
    return config.keyLabelPairs.find((p) => p.key === key);
  }

  function getLabel(key: string): string {
    return findPair(key)?.label || key;
  }

  function getValue(key: string): unknown {
    const pair = findPair(key);
    const value = processedData.value?.[key];

    if ((!value || value === "NA") && pair?.emptyValueBehavior) {
      if (pair.emptyValueBehavior.action === "display") {
        if (pair.emptyValueBehavior.getFallback) {
          const raw = unwrap(resultData);
          return pair.emptyValueBehavior.getFallback(raw || {});
        }
        return pair.emptyValueBehavior.fallback;
      }
      return "";
    }

    return value;
  }

  function shouldDisplay(key: string): boolean {
    const pair = findPair(key);
    if (pair?.emptyValueBehavior?.shouldDisplay) {
      return pair.emptyValueBehavior.shouldDisplay(processedData.value || {});
    }
    return (
      pair?.emptyValueBehavior?.action === "display" ||
      !!processedData.value?.[key]
    );
  }

  function computeTextClasses(key: string, baseClass: string): string[] {
    const pair = findPair(key);
    const value = processedData.value?.[key];
    const isEmpty = !value || value === "NA";
    const emptyClass =
      isEmpty && pair?.emptyValueBehavior?.action === "display"
        ? "text-gray-400"
        : "";
    return [baseClass, "text-sm leading-relaxed whitespace-normal", emptyClass];
  }

  function fieldClasses(key: string): string[] {
    const baseClass = config.valueClassMap[key] || "";
    return computeTextClasses(key, baseClass);
  }

  return {
    processedData,
    getLabel,
    getValue,
    shouldDisplay,
    computeTextClasses,
    fieldClasses,
  };
}
