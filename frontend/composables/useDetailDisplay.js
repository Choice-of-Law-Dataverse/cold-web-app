import { computed } from 'vue'

export function useDetailDisplay(data, config) {
    const computedKeyLabelPairs = computed(() => {
        return config.keyLabelPairs.map((pair) => ({
            ...pair,
            value: data.value?.[pair.key],
        }))
    })

    const valueClassMap = computed(() => {
        return config.valueClassMap
    })

    return {
        computedKeyLabelPairs,
        valueClassMap,
    }
} 