export default defineAppConfig({
  ui: {
    colors: {
      primary: "violet",
      neutral: "slate",
    },
    button: {},
    input: {},
    textarea: {},
    select: {
      variants: {
        variant: {
          outline:
            "bg-white shadow-xs border border-gray-200 hover:border-gray-300 hover:shadow-sm focus:border-[var(--color-cold-purple)] focus:ring-0 transition-all duration-150",
        },
      },
    },
    selectMenu: {
      variants: {
        variant: {
          outline:
            "bg-white shadow-xs border border-gray-200 hover:border-gray-300 hover:shadow-sm focus:border-[var(--color-cold-purple)] focus:ring-0 transition-all duration-150",
        },
      },
      slots: {
        content: "bg-white rounded-lg shadow-lg border border-gray-200 p-1",
        item: "rounded-md px-2.5 py-2 cursor-pointer transition-colors data-highlighted:bg-[var(--gradient-subtle-hover)]",
        input: "border-b border-gray-200 bg-white",
      },
    },
    card: {},
  },
});
