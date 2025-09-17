import { useQuery } from '@tanstack/vue-query'

async function checkTarget(url: string): Promise<boolean> {
  const response = await fetch(
    `/api/check-target?url=${encodeURIComponent(url)}`
  )
  const data = await response.json()
  return data
}

export const useCheckTarget = (url: Ref<string>) => {
  return useQuery({
    queryKey: computed(() => ['verifyPdfLink', url.value]),
    queryFn: () => checkTarget(url.value),
    enabled: computed(() => !!url.value),
  })
}
