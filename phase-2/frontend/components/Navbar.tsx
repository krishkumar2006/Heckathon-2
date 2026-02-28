// frontend/components/Navbar.tsx
// Client Component — top navigation bar with app name, user name, and logout
// Acceptance checks: authClient.signOut() called on logout, redirect to /login after signout

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";

interface NavbarProps {
  userName: string;
}

export default function Navbar({ userName }: NavbarProps) {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await authClient.signOut();
      router.push("/login");
    } catch {
      // Even if signOut fails we redirect — the session will expire naturally
      router.push("/login");
    }
  }

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        {/* Left: App name */}
        <span className="text-base font-bold text-gray-900 tracking-tight">
          Todo App
        </span>

        {/* Right: user name + logout */}
        <div className="flex items-center gap-3 sm:gap-4">
          <span className="hidden text-sm text-gray-600 sm:block">
            {userName}
          </span>
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            aria-label="Sign out"
            className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loggingOut ? "Signing out..." : "Sign out"}
          </button>
        </div>
      </div>
    </nav>
  );
}
