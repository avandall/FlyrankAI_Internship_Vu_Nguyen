/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        foreground: "#f8fafc",
        card: "#111827",
        "card-hover": "#1f2937",
        primary: "#3b82f6",
        "primary-hover": "#2563eb",
        success: "#10b981",
        danger: "#ef4444",
        warning: "#f59e0b",
        border: "#1f293d",
      },
    },
  },
  plugins: [],
}
