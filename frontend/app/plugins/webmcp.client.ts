import { defineNuxtPlugin, useRouter } from "#imports";
import { useApiClient } from "@/composables/useApiClient";
import {
  createWebMcpTools,
  getWebMcpContext,
  registerWebMcpTools,
} from "@/utils/webMcp";

export default defineNuxtPlugin((nuxtApp) => {
  const context = getWebMcpContext();
  if (!context) return;

  const { client } = useApiClient();
  const cleanup = registerWebMcpTools(
    context,
    createWebMcpTools(client, useRouter()),
  );
  nuxtApp.vueApp.onUnmount(cleanup);
  if (import.meta.hot) import.meta.hot.dispose(cleanup);
});
