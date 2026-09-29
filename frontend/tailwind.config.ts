import type { Config } from "tailwindcss";

const config: Config = {
  // Scan every frontend source file that can contain Tailwind classes.
  // Components are critical here because AppShell and the shared UI own
  // the sidebar/layout utilities.
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        ink: "rgb(var(--ink) / <alpha-value>)",
        paper: "rgb(var(--paper) / <alpha-value>)",
        panel: "rgb(var(--panel) / <alpha-value>)",
        line: "rgb(var(--line) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        primary: "rgb(var(--primary) / <alpha-value>)",
        critical: "rgb(var(--critical) / <alpha-value>)",
        amber: "rgb(var(--amber) / <alpha-value>)",
        success: "rgb(var(--success) / <alpha-value>)",
        info: "rgb(var(--info) / <alpha-value>)"
      },
      boxShadow: {
        soft: "0 10px 35px rgba(37, 43, 38, .07)",
        lift: "0 18px 50px rgba(37, 43, 38, .11)"
      },
      fontFamily: {
        display: ["Georgia", "ui-serif", "serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};
export default config;
