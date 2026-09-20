/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gray: {
          850: '#1f2937',
          900: '#111827',
          950: '#030712',
        },
        blue: {
          450: '#3b82f6',
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      scale: {
        '105': '1.05',
      },
    },
  },
  plugins: [],
}
