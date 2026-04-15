/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        safe: '#10b981', // emerald-500
        warning: '#f59e0b', // amber-500
        risk: '#f43f5e', // rose-500
      }
    },
  },
  plugins: [],
}
