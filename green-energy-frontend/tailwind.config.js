/** @type {import('tailwindcss').Config} */
export default {
  // 1. Content Scanning
  // This tells Tailwind to look at all your .jsx and .html files
  // for class names.
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  
  // 2. Theme Extension (P1 - D.R.Y. Principle)
  // We define the project's custom colors here so we can reuse them
  // with classes like `bg-brand-green` or `text-brand-pink`.
  theme: {
    extend: {
      colors: {
        // Naming based on Figma design
        'brand-cream': '#FDFCF5', // Main page background
        'brand-green': '#34A853', // Header background & links
        'brand-pink': '#E5409A',  // Primary button pink
      },
      fontFamily: {
        // Ensures Tailwind uses the 'Inter' font we loaded in index.html
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        // A custom value to match the large curve on the auth header
        '4xl': '3rem', 
      }
    },
  },
  plugins: [],
}