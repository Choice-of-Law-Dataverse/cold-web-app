import { type Ref } from 'vue'
import { useFullTable } from '@/composables/useFullTable'

type Options = {
  enableErrorHandling?: boolean
  redirectOnNotFound?: boolean
  showToast?: boolean
}

export function useSpecialists(
  jurisdictionName: Ref<string>,
  options: Options = {}
) {
  return useFullTable('Specialists', {
    ...options,
    filters: [{ column: 'Jurisdiction', value: jurisdictionName.value }],
  })
}
