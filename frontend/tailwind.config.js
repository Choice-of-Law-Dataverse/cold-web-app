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
        'cold-night-alpha': '#0F003580', // 50% alpha; https://gist.github.com/lopspower/03fb1cc0ac9f32ef38f4
        'cold-night-alpha-25': '#0F003540', // 25% alpha
        'cold-black': '#262626',
        
        'cold-bg': '#FAFAFA',
        'cold-gray': '#E2E8F0',
        'cold-gray-alpha': '#E2E8F080', // 50% alpha
        
        'label-question': '#FFA8FB',
        'label-question-alpha': '#FFA8FB1A', // 10% alpha
        
        'label-court-decision': '#FF7167',
        'label-court-decision-alpha': '#FF71671A', // 10% alpha
        
        'label-legal-instrument': '#FF9D00',
        'label-legal-instrument-alpha': '#FF9D001A', // 10% alpha
        
        'label-literature': '#4DC3FA',
        'label-literature-alpha': '#4DC3FA1A', // 10% alpha
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
          '--color-cold-purple': theme('colors.cold-purple'),
          '--color-cold-night': theme('colors.cold-night'),
          '--color-cold-night-alpha': theme('colors.cold-night-alpha'),
          '--color-cold-night-alpha-25': theme('colors.cold-night-alpha-25'),
          
          '--color-cold-gray': theme('colors.cold-gray'),
          '--color-cold-gray-alpha': theme('colors.cold-gray-alpha'),
          
          '--color-label-question': theme('colors.label-question'),
          '--color-label-question-alpha': theme('colors.label-question-alpha'),
          
          '--color-label-court-decision': theme('colors.label-court-decision'),
          '--color-label-court-decision-alpha': theme('colors.label-court-decision-alpha'),
          
          '--color-label-legal-instrument': theme('colors.label-legal-instrument'),
          '--color-label-legal-instrument-alpha': theme('colors.label-legal-instrument-alpha'),
          
          '--color-label-literature': theme('colors.label-literature'),
          '--color-label-literature-alpha': theme('colors.label-literature-alpha'),
        },
      })
    },
  ],
}
