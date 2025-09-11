import { useFullTable } from '@/composables/useFullTable'

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  return useFullTable('Literature', {
    filters: [
      {
        column: 'Jurisdiction',
        value: jurisdiction.value,
      },
    ],
  })
}
