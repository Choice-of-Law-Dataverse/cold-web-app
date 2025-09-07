import { useQuery } from "@tanstack/vue-query";

async function verify(url: string): Promise<boolean> {
  const response = await fetch(`/api/check-pdf-exists?url=${encodeURIComponent(url)}`, { method: 'HEAD' });
  return response.ok
}

export const useVerifyPdfLink = (url: Ref<string>) => {
  return useQuery({
    queryKey: computed(() => ["verifyPdfLink", url.value]),
    queryFn: () => verify(url.value),
    enabled: computed(() => !!url.value),
  });
};
