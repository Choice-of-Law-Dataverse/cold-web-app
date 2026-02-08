export default defineAppConfig({
  ui: {
    colors: {
      primary: "violet",
      secondary: "cyan",
      neutral: "slate",
    },
    button: {
      compoundVariants: [
        {
          color: "neutral" as const,
          variant: "outline" as const,
          class: {
            base: "group cursor-pointer uppercase gap-0 py-[0.375rem] px-3 hover:bg-inverted hover:text-inverted hover:ring-inverted active:bg-inverted active:text-inverted",
            leadingIcon:
              "size-3 mr-1.5 opacity-100 transition-all duration-200 group-hover:size-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "size-0 ml-0 opacity-0 transition-all duration-200 group-hover:size-3 group-hover:ml-1.5 group-hover:opacity-100",
          },
        },
        {
          color: "secondary" as const,
          variant: "subtle" as const,
          class: {
            base: "group cursor-pointer uppercase py-[0.375rem] px-3 ring-0 bg-secondary/5 hover:bg-secondary/10 border border-secondary/20 hover:border-secondary/35 hover:shadow-sm focus-visible:ring-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary",
            trailingIcon:
              "w-0 opacity-0 transition-all duration-200 group-hover:w-4 group-hover:opacity-100",
          },
        },
        {
          color: "neutral" as const,
          variant: "soft" as const,
          class: {
            base: "landing-item-button flex w-full overflow-hidden rounded-lg shadow-xs [background:var(--gradient-subtle)] gap-3 py-3 px-4 pl-5 text-left font-medium transition-all duration-150 hover:shadow-sm hover:[background:var(--gradient-subtle-emphasis)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-cold-purple)]",
            label: "contents",
          },
        },
        {
          color: "primary" as const,
          variant: "link" as const,
          class: "font-medium",
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
