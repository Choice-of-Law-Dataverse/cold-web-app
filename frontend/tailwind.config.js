/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{vue,js}',
    './layouts/**/*.{vue,js}',
    './pages/**/*.{vue,js}',
    './plugins/**/*.{js,ts}',
    './nuxt.config.{js,ts}',
  ],
  theme: {
    extend: {
      colors: {
        'cold-purple': '#6F4DFA',
        'cold-green': '#4DFAB2',
        'cold-night': '#0F0035',
        'cold-black': '#262626',
        'cold-bg': '#FAFAFA',
        'cold-gray': '#E2E8F0',
        'label-question': '#FFA8FB',
        'label-court-decision': '#FF7167',
        'label-legal-instrument': '#FF9D00',
        'label-literature': '#4DC3FA',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    function({ addBase, theme }) {
      // Generate CSS variables for colors
      addBase({
        ':root': {
          '--color-cold-gray': theme('colors.cold-gray'),
        },
      })
    },
  ],
}
