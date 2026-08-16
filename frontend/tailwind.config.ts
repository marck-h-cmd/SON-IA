import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#00A9E0",
        primaryHover: "#0084B4",
        secondary: "#6B7280",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        info: "#00A9E0",
        movistar: {
          50: "#F0F9FF",
          100: "#EBF7FC",
          200: "#BAE6FD",
          300: "#7DD3FC",
          400: "#38BDF8",
          500: "#00A9E0",
          600: "#0084B4",
          700: "#0369A1",
          800: "#075985",
          900: "#0C4A6E",
          950: "#082F49",
          DEFAULT: "#00A9E0",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
  darkMode: "class",
}
export default config
