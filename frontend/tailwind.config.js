/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './components/**/*.{vue,js}',
    './layouts/**/*.{vue,js}',
    './pages/**/*.{vue,js}',
    './plugins/**/*.{js,ts}',
    './nuxt.config.{js,ts}',
  ],
  safelist: [
    'md:col-span-1',
    'md:col-span-2',
    'md:col-span-3',
    'md:col-span-4',
    'md:col-span-5',
    'md:col-start-1',
    'md:col-start-2',
    'md:col-start-3',
    'md:col-start-4',
    'md:col-start-5',
    'md:col-start-6',
    'md:col-start-7',
    'md:col-start-8',
    'md:col-start-8',
    'md:col-start-10',
  ],
  theme: {
    extend: {
      colors: {
        'cold-purple': '#6F4DFA',
        'cold-purple-alpha': '#6F4DFA0D', // 5% alpha
        'cold-purple-fake-alpha': '#f3f2fa', // 100% alpha but same color as cold-purple-alpha
        'cold-green': '#4DFAB2',
        'cold-green-alpha': '#4DFAB280',
        'cold-cream': '#FFF0D9',
        'cold-night': '#0F0035',
        'cold-night-alpha': '#0F003580', // 50% alpha; https://gist.github.com/lopspower/03fb1cc0ac9f32ef38f4
        'cold-night-alpha-25': '#0F003540', // 25% alpha
        'cold-black': '#262626',
        
        'cold-bg': '#FAFAFA',
        'cold-gray': '#E2E8F0',
        'cold-gray-alpha': '#E2E8F080', // 50% alpha
        'cold-dark-gray': '#F1F3F7', 
        
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
          '--color-cold-purple-alpha': theme('colors.cold-purple-alpha'),
          '--color-cold-purple-fake-alpha': theme('colors.cold-purple-fake-alpha'),
          '--color-cold-green': theme('colors.cold-green'),
          '--color-cold-green-alpha': theme('colors.cold-green-alpha'),
          '--color-cold-cream': theme('colors.cold-cream'),
          '--color-cold-night': theme('colors.cold-night'),
          '--color-cold-night-alpha': theme('colors.cold-night-alpha'),
          '--color-cold-night-alpha-25': theme('colors.cold-night-alpha-25'),
          
          '--color-cold-gray': theme('colors.cold-gray'),
          '--color-cold-gray-alpha': theme('colors.cold-gray-alpha'),
          '--cold-dark-gray': theme('colors.cold-dark-gray'),
          
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
