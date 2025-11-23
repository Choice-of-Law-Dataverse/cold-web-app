export default defineAppConfig({
  ui: {
    card: {
      variants: {
        variant: {
          outline: {
            root: "bg-default ring-1 ring-[var(--color-cold-gray)] divide-y divide-[var(--color-cold-gray)]",
          },
        },
      },
      defaultVariants: {
        variant: "outline",
      },
      slots: {
        root: "overflow-hidden rounded-none shadow-none",
        header: "p-4 sm:px-6",
        body: "p-4 sm:p-6",
        footer: "p-4 sm:px-6",
      },
    },
    colors: {
      primary: "violet",
      neutral: "slate",
    },
  },
});
