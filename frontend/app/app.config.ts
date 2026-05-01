export default defineAppConfig({
  ui: {
    colors: {
      primary: "violet",
      secondary: "teal",
      neutral: "slate",
    },
    button: {
      compoundVariants: [
        {
          color: "success" as const,
          variant: "solid" as const,
          class: {
            base: "bg-[var(--color-cold-green)] text-white",
          },
        },
        {
          color: "neutral" as const,
          variant: "outline" as const,
          class: {
            base: "group cursor-pointer uppercase gap-0 py-[0.375rem] px-3 hover:bg-inverted hover:text-inverted hover:ring-inverted active:bg-inverted active:text-inverted",
            leadingIcon:
              "h-3 w-3 mr-1.5 opacity-100 transition-[width,margin,opacity] duration-200 group-hover:w-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "h-3 w-0 ml-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-3 group-hover:ml-1.5 group-hover:opacity-100",
          },
        },
        {
          color: "secondary" as const,
          variant: "subtle" as const,
          class: {
            base: "group cursor-pointer uppercase gap-0 py-[0.375rem] px-3 bg-secondary/5 hover:bg-secondary/10 border border-secondary/20 hover:border-secondary/35",
            leadingIcon:
              "h-3 w-3 mr-1.5 opacity-100 transition-[width,margin,opacity] duration-200 group-hover:w-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "h-3 w-0 ml-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-3 group-hover:ml-1.5 group-hover:opacity-100",
          },
        },
        {
          color: "neutral" as const,
          variant: "soft" as const,
          class: {
            base: "landing-item-button flex w-full overflow-hidden rounded-lg [background:var(--gradient-subtle)] gap-3 py-3 px-4 pl-5 text-left font-medium transition-all duration-150 hover:shadow-xs hover:[background:var(--gradient-subtle-emphasis)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-cold-purple)]",
            label: "contents",
            leadingIcon:
              "h-3 w-3 mr-1.5 opacity-100 transition-[width,margin,opacity] duration-200 group-hover:w-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "h-3 w-0 ml-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-3 group-hover:ml-1.5 group-hover:opacity-100",
          },
        },
        {
          color: "primary" as const,
          variant: "ghost" as const,
          class: {
            base: "group cursor-pointer gap-0 rounded-lg px-3 py-1.5 text-sm font-medium ring-0 [background:var(--gradient-subtle)] text-[var(--color-cold-night)] transition-all duration-150 hover:[background:white] hover:shadow-xs hover:text-[var(--color-cold-purple)] hover:ring-0",
            leadingIcon:
              "h-4 w-4 mr-2 shrink-0 opacity-100 transition-[width,margin,opacity] duration-200 group-hover:w-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "h-4 w-0 ml-0 shrink-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-4 group-hover:ml-2 group-hover:opacity-100",
          },
        },
        {
          color: "primary" as const,
          variant: "link" as const,
          class: "font-medium",
        },
        {
          color: "neutral" as const,
          variant: "ghost" as const,
          class: "cursor-pointer",
        },
        {
          color: "neutral" as const,
          variant: "ghost" as const,
          size: "xs" as const,
          class: {
            base: "group gap-0",
            leadingIcon:
              "h-3 w-3 mr-1.5 opacity-100 transition-[width,margin,opacity] duration-200 group-hover:w-0 group-hover:mr-0 group-hover:opacity-0",
            trailingIcon:
              "h-3 w-0 ml-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-3 group-hover:ml-1.5 group-hover:opacity-100",
          },
        },
      ],
    },
    input: {
      slots: {
        root: "w-full",
        base: "h-[42px] px-3 border border-black/[0.06] rounded-lg bg-white text-[var(--color-cold-night)] text-sm leading-[1.4] transition-all duration-150 placeholder:text-[var(--color-cold-night-alpha-50,#8193a8)] hover:border-black/[0.12] focus:border-[var(--color-cold-purple)] focus:bg-white disabled:bg-[var(--color-cold-gray-alpha)] disabled:text-[var(--color-cold-night-alpha)] disabled:cursor-not-allowed",
      },
    },
    textarea: {
      slots: {
        root: "w-full",
        base: "min-h-24 px-3 py-2.5 border border-black/[0.06] rounded-lg bg-white text-[var(--color-cold-night)] text-sm leading-[1.4] transition-all duration-150 resize-y placeholder:text-[var(--color-cold-night-alpha-50,#8193a8)] hover:border-black/[0.12] focus:border-[var(--color-cold-purple)] focus:bg-white disabled:bg-[var(--color-cold-gray-alpha)] disabled:text-[var(--color-cold-night-alpha)] disabled:cursor-not-allowed",
      },
    },
    select: {
      variants: {
        variant: {
          outline:
            "bg-white border border-black/[0.06] hover:border-black/[0.12] focus:border-[var(--color-cold-purple)] focus:ring-0 transition-all duration-150",
        },
      },
    },
    selectMenu: {
      variants: {
        variant: {
          outline:
            "bg-white border border-black/[0.06] hover:border-black/[0.12] focus:border-[var(--color-cold-purple)] focus:ring-0 transition-all duration-150",
        },
      },
      slots: {
        content: "bg-white rounded-lg shadow-md border border-black/[0.06] p-1",
        item: "rounded-md px-2.5 py-2 cursor-pointer transition-colors data-highlighted:bg-[var(--gradient-subtle-hover)]",
        input: "border-b border-black/[0.06] bg-white",
      },
    },
    card: {
      slots: {
        root: "rounded-lg overflow-hidden relative bg-white border-0 ring-0",
      },
      variants: {
        variant: {
          outline: {
            root: "bg-white ring-0 divide-y-0",
          },
          subtle: {
            root: "ring-0",
          },
        },
      },
    },
  },
});
