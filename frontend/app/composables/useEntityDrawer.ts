import { ref } from "vue";
import type { TableName } from "@/types/api";

const MOBILE_BREAKPOINT = 640;

interface DrawerEntity {
  coldId: string;
  table: TableName;
  basePath: string;
}

const isOpen = ref(false);
const entity = ref<DrawerEntity | null>(null);

export function useEntityDrawer() {
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
    entity.value = { coldId, table, basePath };
    if (!isOpen.value) {
      isOpen.value = true;
    }
  }

  function closeDrawer() {
    isOpen.value = false;
  }

  return { isOpen, entity, openDrawer, closeDrawer };
}
