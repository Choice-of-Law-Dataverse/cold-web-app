import { computed } from 'vue'

export function useDetailDisplay(data, keyLabelPairs) {
    const computedKeyLabelPairs = computed(() => {
        return keyLabelPairs.map((pair) => ({
            ...pair,
            value: data.value?.[pair.key],
        }))
    })

    const valueClassMap = computed(() => {
        const map = {}
        keyLabelPairs.forEach((pair) => {
            if (pair.key === 'Case Title' || pair.key === 'Title (in English)' || pair.key === 'Title') {
                map[pair.key] = 'result-value-medium'
            } else if (['Abstract', 'Text of the Relevant Legal Provisions'].includes(pair.key)) {
                map[pair.key] = 'result-value-small'
            }
        })
        return map
    })

    return {
        computedKeyLabelPairs,
        valueClassMap,
    }
} 