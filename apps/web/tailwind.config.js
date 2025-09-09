import defaultTheme from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config}; */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "./**/components/ui/**/*.{ts,tsx}",
    "./apps/web/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Presentation","var(--font-sans)",...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [],
}
