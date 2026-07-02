/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#FAFAF8",
        panel: "#F4F2EC",
        panelHover: "#ECE9E1",
        border: "#E6E2D8",
        ink: "#171512",
        muted: "#78746B",
        accent: "#5B4BDB",
        accentSoft: "#EEEBFB",
        accentDim: "#4A3DC0",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 2px rgba(23, 21, 18, 0.04)",
        float: "0 8px 30px rgba(23, 21, 18, 0.08)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
