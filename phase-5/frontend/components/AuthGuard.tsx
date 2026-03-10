"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { isTokenValid } from "@/lib/auth-utils";

interface AuthGuardProps {
  children: ReactNode;
}

/**
 * AuthGuard component that redirects unauthenticated users to signin.
 * Wraps protected pages to ensure only logged-in users can access them.
 * Includes token expiration validation.
 */
export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Check for valid auth token (including expiration)
    if (!isTokenValid()) {
      // Clear any invalid token
      localStorage.removeItem("auth_token");
      // Redirect to signin
      router.push("/signin");
      return;
    }

    // Token is valid
    setIsAuthenticated(true);
  }, [router]);

  // Show loading while checking auth - with enhanced styling
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
        <div className="text-center">
          <div className="relative">
            {/* Outer glow ring */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 blur-lg opacity-50 animate-pulse"></div>
            {/* Spinner */}
            <svg
              className="relative w-12 h-12 spinner-glow"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="url(#gradient)"
                strokeWidth="3"
              />
              <path
                className="opacity-75"
                fill="url(#gradient)"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <p className="mt-4 text-sm text-slate-400">Authenticating...</p>
        </div>
      </div>
    );
  }

  // Show nothing if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  // Render children if authenticated
  return <>{children}</>;
}
