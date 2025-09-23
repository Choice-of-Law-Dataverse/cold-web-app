import { computed, type Ref } from 'vue'
import { useRecordDetailsList } from '@/composables/useRecordDetails'

export function useLiteratures(ids: Ref<string>) {
  const literatureIds = computed(() =>
    ids.value
      ? ids.value
          .split(',')
          .map((id: string) => id.trim())
          .filter((id: string) => id)
      : []
  )

  return useRecordDetailsList(
    computed(() => 'Literature'),
    literatureIds
  )
}
