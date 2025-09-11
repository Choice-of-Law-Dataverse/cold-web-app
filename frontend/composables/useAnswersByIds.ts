import { computed, type Ref } from 'vue'
import { useRecordDetailsList } from '@/composables/useRecordDetails'

export function useAnswersByIds(
  ids: Ref<Array<string | number>>,
  enabled: Ref<boolean> | boolean = true
) {
  const filteredIds = computed(() =>
    (enabled ? ids.value || [] : []).filter(Boolean)
  )

  const results = useRecordDetailsList(
    computed(() => 'Answers'),
    filteredIds
  )

  const data = computed<Record<string | number, string | null>>(() => {
    const map: Record<string | number, string | null> = {}
    const records = results.data.value as unknown as
      | Record<string | number, { Answer?: string }>
      | undefined
    filteredIds.value.forEach((id) => {
      const rec = records?.[id]
      map[id] = rec?.Answer ?? null
    })
    return map
  })

  return { ...results, data }
}
