import { computed, type Ref } from "vue";

interface KeyLabelPair {
  key: string;
  label?: string;
  tooltip?: string;
  emptyValueBehavior?: string | Record<string, unknown>;
  value?: unknown;
  [key: string]: unknown;
}

interface Config {
  keyLabelPairs: KeyLabelPair[];
  valueClassMap: Record<string, string>;
}

export function useDetailDisplay(
  data: Ref<Record<string, unknown> | null | undefined>,
  config: Config,
) {
  const computedKeyLabelPairs = computed(() => {
    return config.keyLabelPairs.map((pair) => ({
      ...pair,
      value: data.value?.[pair.key],
    }));
  });

  const valueClassMap = computed(() => {
    return config.valueClassMap;
  });

  return {
    computedKeyLabelPairs,
    valueClassMap,
  };
}
