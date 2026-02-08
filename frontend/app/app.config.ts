export default defineAppConfig({
  ui: {
    colors: {
      primary: "violet",
      neutral: "slate",
    },
    button: {
      compoundVariants: [
        {
          color: "neutral" as const,
          variant: "outline" as const,
          class:
            "uppercase ring ring-inset ring-accented text-default bg-default hover:bg-inverted hover:text-inverted hover:ring-inverted active:bg-inverted active:text-inverted disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted",
        },
      ],
    },
    input: {
      slots: {
        root: "w-full",
        base: "h-[42px] px-3 border border-gray-200 rounded-lg bg-white text-[var(--color-cold-night)] text-sm leading-[1.4] shadow-xs transition-all duration-150 placeholder:text-[var(--color-cold-night-alpha-50,#8193a8)] hover:border-gray-300 hover:shadow-sm focus:border-[var(--color-cold-purple)] focus:bg-white focus:shadow-sm disabled:bg-[var(--color-cold-gray-alpha)] disabled:text-[var(--color-cold-night-alpha)] disabled:cursor-not-allowed",
      },
    },
    textarea: {
      slots: {
        root: "w-full",
        base: "min-h-24 px-3 py-2.5 border border-gray-200 rounded-lg bg-white text-[var(--color-cold-night)] text-sm leading-[1.4] shadow-xs transition-all duration-150 resize-y placeholder:text-[var(--color-cold-night-alpha-50,#8193a8)] hover:border-gray-300 hover:shadow-sm focus:border-[var(--color-cold-purple)] focus:bg-white focus:shadow-sm disabled:bg-[var(--color-cold-gray-alpha)] disabled:text-[var(--color-cold-night-alpha)] disabled:cursor-not-allowed",
      },
    },
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
    card: {
      slots: {
        root: "rounded-lg overflow-hidden relative bg-white border-0 ring-0",
      },
    },
  },
});
