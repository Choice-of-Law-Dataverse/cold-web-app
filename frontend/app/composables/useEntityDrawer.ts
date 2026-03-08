import { ref, computed } from "vue";
import type { TableName } from "@/types/api";

const MOBILE_BREAKPOINT = 640;
const MAX_HISTORY = 3;

interface DrawerEntity {
  coldId: string;
  table: TableName;
  basePath: string;
}

const isOpen = ref(false);
const entity = ref<DrawerEntity | null>(null);
const history = ref<DrawerEntity[]>([]);

export function useEntityDrawer() {
  const canGoBack = computed(() => history.value.length > 0);

  function openDrawer(
    coldId: string,
    table: TableName,
    basePath: string,
    forceDrawer = false,
  ) {
    if (!forceDrawer && window.innerWidth < MOBILE_BREAKPOINT) {
      const path = coldId.startsWith("/") ? coldId : `${basePath}/${coldId}`;
      navigateTo(path);
      return;
    }
    if (entity.value) {
      history.value = [...history.value, entity.value].slice(-MAX_HISTORY);
    }
    entity.value = { coldId, table, basePath };
    if (!isOpen.value) {
      isOpen.value = true;
    }
  }

  function goBack() {
    if (history.value.length === 0) return;
    const previous = history.value[history.value.length - 1]!;
    history.value = history.value.slice(0, -1);
    entity.value = previous;
  }

  function closeDrawer() {
    isOpen.value = false;
    history.value = [];
  }

  return { isOpen, entity, canGoBack, openDrawer, closeDrawer, goBack };
}
