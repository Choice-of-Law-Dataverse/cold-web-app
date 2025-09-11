import { useFullTable } from '@/composables/useFullTable'

export function useInternationalLegalProvisions() {
  return useFullTable('International Legal Provisions', {
    select: (data) => {
      return data.slice().sort((a: any, b: any) => {
        const aOrder =
          typeof a['Interface Order'] === 'number'
            ? a['Interface Order']
            : Number(a['Interface Order']) || 0
        const bOrder =
          typeof b['Interface Order'] === 'number'
            ? b['Interface Order']
            : Number(b['Interface Order']) || 0
        return aOrder - bOrder
      })
    },
  })
}
