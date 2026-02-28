// frontend/app/dashboard/page.tsx
// Client Component — protected dashboard with task management
// Acceptance checks: session checked via useSession(), redirect if unauthenticated,
//                    TaskForm + TaskList wired with refreshKey, filter buttons styled

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import Navbar from "@/components/Navbar";
import TaskForm from "@/components/TaskForm";
import TaskList from "@/components/TaskList";

type FilterValue = "all" | "pending" | "completed";

const FILTER_OPTIONS: { label: string; value: FilterValue }[] = [
  { label: "All", value: "all" },
  { label: "Pending", value: "pending" },
  { label: "Completed", value: "completed" },
];

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  const [activeFilter, setActiveFilter] = useState<FilterValue>("all");
  const [refreshKey, setRefreshKey] = useState(0);

  // Acceptance check: redirect to /login when session is absent and not loading
  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [isPending, session, router]);

  // ---------------------------------------------------------------------------
  // Loading state — session check in progress
  // ---------------------------------------------------------------------------
  if (isPending) {
    return (
      <div
        className="flex min-h-screen items-center justify-center bg-gray-50"
        aria-live="polite"
        aria-label="Authenticating"
      >
        <div className="flex flex-col items-center gap-3 text-gray-400">
          <svg
            className="h-8 w-8 animate-spin text-blue-500"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <p className="text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  // Acceptance check: render nothing while redirect is in flight
  if (!session) {
    return null;
  }

  const userId = session.user.id;
  const userName = session.user.name ?? session.user.email;

  return (
    <>
      <Navbar userName={userName} />

      {/* Top padding clears the fixed navbar (h-14 = 56px) */}
      <main className="mx-auto max-w-5xl px-4 pt-20 pb-12 sm:px-6">
        {/* Page heading */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Your tasks</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and track your todos below.
          </p>
        </div>

        {/* Task creation form */}
        <TaskForm
          userId={userId}
          onTaskCreated={() => setRefreshKey((k) => k + 1)}
        />

        {/* Filter buttons */}
        <div
          className="mb-5 flex gap-2"
          role="group"
          aria-label="Filter tasks by status"
        >
          {FILTER_OPTIONS.map(({ label, value }) => (
            <button
              key={value}
              onClick={() => setActiveFilter(value)}
              aria-pressed={activeFilter === value}
              className={`rounded-lg border px-4 py-1.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                activeFilter === value
                  ? "border-blue-600 bg-blue-600 text-white"
                  : "border-gray-300 bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Task list */}
        <TaskList
          userId={userId}
          filter={activeFilter}
          refreshKey={refreshKey}
        />
      </main>
    </>
  );
}
