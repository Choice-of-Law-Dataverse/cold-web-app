import { computed, type Ref } from 'vue'
import { useRecordDetailsList } from '@/composables/useRecordDetails'

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useLiteratures(
  ids: Ref<string>,
  options: Options = {}
) {
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
    literatureIds,
    options
  )
}
