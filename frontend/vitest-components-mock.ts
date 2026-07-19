import { defineComponent } from "vue";

export const NuxtLink = defineComponent({
  name: "NuxtLink",
  template: "<a><slot /></a>",
});
