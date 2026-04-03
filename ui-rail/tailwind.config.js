/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'pulse-blue': 'pulse-blue 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'pulse-blue': {
          '0%, 100%': { opacity: 1, color: 'rgb(96 165 250)' },
          '50%': { opacity: .5, color: 'rgb(30 58 138)' },
        }
      }
    },
  },
  plugins: [
    require("tailwindcss-animate"),
  ],
}
