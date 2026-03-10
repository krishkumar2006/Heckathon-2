import type { NextConfig } from "next";

// Render backend URL — set NEXT_PUBLIC_API_URL in Vercel env vars
const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || "http://localhost:8000";

const isDocker = process.env.DOCKER_BUILD === "true";

const nextConfig: NextConfig = {
  devIndicators: false,

  // standalone only for Docker — not for Vercel
  ...(isDocker && { output: "standalone" }),

  // Proxy /api to backend (works on Vercel too)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
