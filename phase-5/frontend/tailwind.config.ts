import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette - Neon 3D Theme
        primary: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#bf00ff",
          600: "#9900cc",
          700: "#7700aa",
          800: "#550088",
          900: "#330055",
        },
        accent: {
          pink: "#ff006e",
          cyan: "#00f5ff",
          indigo: "#3d5afe",
          gold: "#ffd700",
        },
        neon: {
          cyan: "#00f5ff",
          purple: "#bf00ff",
          pink: "#ff006e",
          blue: "#3d5afe",
        },
        dark: {
          900: "#080818",
          800: "#100820",
          700: "#180c30",
          600: "#201040",
        },
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
        "neon-purple": "0 0 20px rgba(139, 92, 246, 0.5), 0 0 40px rgba(139, 92, 246, 0.3)",
        "neon-pink": "0 0 20px rgba(236, 72, 153, 0.5), 0 0 40px rgba(236, 72, 153, 0.3)",
        "neon-cyan": "0 0 20px rgba(6, 182, 212, 0.5), 0 0 40px rgba(6, 182, 212, 0.3)",
        "3d": "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)",
        "3d-hover": "0 25px 50px -12px rgba(0, 0, 0, 0.4)",
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "gradient-shift": "gradient-shift 8s ease infinite",
        "slide-up": "slide-up 0.5s ease-out",
        "bounce-in": "bounce-in 0.6s ease-out",
        "fade-in": "fade-in 0.3s ease-out",
        "typing-dot": "typing-dot 1.4s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(139, 92, 246, 0.5)" },
          "50%": { boxShadow: "0 0 40px rgba(139, 92, 246, 0.8), 0 0 60px rgba(236, 72, 153, 0.4)" },
        },
        "gradient-shift": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "slide-up": {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "bounce-in": {
          "0%": { transform: "scale(0.3)", opacity: "0" },
          "50%": { transform: "scale(1.05)" },
          "70%": { transform: "scale(0.9)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "typing-dot": {
          "0%, 60%, 100%": { transform: "translateY(0)" },
          "30%": { transform: "translateY(-10px)" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-mesh":
          "radial-gradient(at 40% 20%, hsla(280, 100%, 70%, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(320, 100%, 60%, 0.1) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(220, 100%, 60%, 0.1) 0px, transparent 50%), radial-gradient(at 80% 50%, hsla(340, 100%, 60%, 0.1) 0px, transparent 50%), radial-gradient(at 0% 100%, hsla(260, 100%, 60%, 0.1) 0px, transparent 50%), radial-gradient(at 80% 100%, hsla(200, 100%, 60%, 0.1) 0px, transparent 50%)",
      },
    },
  },
  plugins: [],
};
export default config;
