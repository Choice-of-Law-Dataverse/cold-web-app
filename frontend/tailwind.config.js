/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{vue,js}",
    "./layouts/**/*.{vue,js}",
    "./pages/**/*.{vue,js}",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
  ],
  safelist: [
    "md:col-span-1",
    "md:col-span-2",
    "md:col-span-3",
    "md:col-span-4",
    "md:col-span-5",
    "md:col-span-6",
    "md:col-span-7",
    "md:col-span-8",
    "md:col-start-1",
    "md:col-start-2",
    "md:col-start-3",
    "md:col-start-4",
    "md:col-start-5",
    "md:col-start-6",
    "md:col-start-7",
    "md:col-start-8",
    "md:col-start-8",
    "md:col-start-10",
  ],
  theme: {
    extend: {
      maxWidth: {
        container: "var(--container-width)",
      },
      colors: {
        "cold-purple": "#6F4DFA",
        "cold-purple-alpha": "#6F4DFA0D",
        "cold-purple-alpha-25": "#6F4DFA40",
        "cold-purple-fake-alpha": "#f3f2fa",
        "cold-green": "#4DFAB2",
        "cold-green-alpha": "#4DFAB280",
        "cold-green-alpha-10": "#4DFAB21A",
        "cold-cream": "#FFF0D9",
        "cold-night": "#0F0035",
        "cold-night-alpha": "#0F003580",
        "cold-night-alpha-25": "#0F003540",
        "cold-black": "#262626",

        "cold-bg": "#FAFAFA",
        "cold-gray": "#E2E8F0",
        "cold-gray-alpha": "#E2E8F080",
        "cold-dark-gray": "#F1F3F7",

        "cold-slate": "#64748B",
        "cold-teal": "#0891B2",
        "cold-charcoal": "#6B7280",

        "label-question": "#0e7490", // darker teal
        "label-question-alpha": "#0e74901A",

        "label-court-decision": "#b85a42", // darker coral
        "label-court-decision-alpha": "#b85a421A",

        "label-instrument": "#2a7a5a", // darker green
        "label-instrument-alpha": "#2a7a5a1A",

        "label-literature": "#a07830", // darker golden
        "label-literature-alpha": "#a078301A",

        "label-arbitration": "#5a6ab8", // darker indigo
        "label-arbitration-alpha": "#5a6ab81A",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/aspect-ratio"),
    function ({ addBase, theme }) {
      addBase({
        ":root": {
          "--color-cold-purple": theme("colors.cold-purple"),
          "--color-cold-purple-alpha": theme("colors.cold-purple-alpha"),
          "--color-cold-purple-alpha-25": theme("colors.cold-purple-alpha-25"),
          "--color-cold-purple-fake-alpha": theme(
            "colors.cold-purple-fake-alpha",
          ),
          "--color-cold-green": theme("colors.cold-green"),
          "--color-cold-green-alpha": theme("colors.cold-green-alpha"),
          "--color-cold-green-alpha-10": theme("colors.cold-green-alpha-10"),
          "--color-cold-cream": theme("colors.cold-cream"),
          "--color-cold-night": theme("colors.cold-night"),
          "--color-cold-night-alpha": theme("colors.cold-night-alpha"),
          "--color-cold-night-alpha-25": theme("colors.cold-night-alpha-25"),

          "--color-cold-gray": theme("colors.cold-gray"),
          "--color-cold-gray-alpha": theme("colors.cold-gray-alpha"),
          "--cold-dark-gray": theme("colors.cold-dark-gray"),

          "--color-cold-slate": theme("colors.cold-slate"),
          "--color-cold-teal": theme("colors.cold-teal"),
          "--color-cold-charcoal": theme("colors.cold-charcoal"),

          "--color-label-question": theme("colors.label-question"),
          "--color-label-question-alpha": theme("colors.label-question-alpha"),

          "--color-label-court-decision": theme("colors.label-court-decision"),
          "--color-label-court-decision-alpha": theme(
            "colors.label-court-decision-alpha",
          ),

          "--color-label-instrument": theme("colors.label-instrument"),
          "--color-label-instrument-alpha": theme(
            "colors.label-instrument-alpha",
          ),

          "--color-label-literature": theme("colors.label-literature"),
          "--color-label-literature-alpha": theme(
            "colors.label-literature-alpha",
          ),

          "--color-label-arbitration": theme("colors.label-arbitration"),
          "--color-label-arbitration-alpha": theme(
            "colors.label-arbitration-alpha",
          ),
        },
      });
    },
  ],
};
