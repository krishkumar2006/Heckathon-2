// frontend/components/TaskList.tsx
// Client Component — fetches and renders the task list with loading/error/empty states
// Acceptance checks: spinner on load, error message on failure, empty state, sorted newest first

"use client";

import { useEffect, useState } from "react";
import type { Task } from "@/types/task";
import * as api from "@/lib/api";
import TaskCard from "@/components/TaskCard";

interface TaskListProps {
  userId: string;
  filter: "all" | "pending" | "completed";
  refreshKey: number;
}

export default function TaskList({ userId, filter, refreshKey }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Internal counter to trigger re-fetch after individual task updates (edit/delete/toggle)
  const [refetchCount, setRefetchCount] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function fetchTasks() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getTasks(userId, filter);
        if (!cancelled) {
          // Acceptance check: sort newest first
          const sorted = [...data].sort(
            (a, b) =>
              new Date(b.created_at).getTime() -
              new Date(a.created_at).getTime()
          );
          setTasks(sorted);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : "Failed to load tasks.";
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void fetchTasks();

    return () => {
      cancelled = true;
    };
  }, [userId, filter, refreshKey, refetchCount]);

  function handleTaskUpdate() {
    setRefetchCount((c) => c + 1);
  }

  // ---------------------------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------------------------
  if (loading) {
    return (
      <div
        className="flex flex-col items-center justify-center py-16 text-gray-400"
        aria-live="polite"
        aria-label="Loading tasks"
      >
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
        <p className="mt-3 text-sm">Loading tasks...</p>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Error state
  // ---------------------------------------------------------------------------
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700"
      >
        <p className="font-medium">Failed to load tasks</p>
        <p className="mt-1 text-red-600">{error}</p>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Empty state
  // ---------------------------------------------------------------------------
  if (tasks.length === 0) {
    return (
      <div
        className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center"
        aria-live="polite"
      >
        <p className="text-sm text-gray-500">
          {filter === "all"
            ? "No tasks yet. Create your first task above!"
            : filter === "pending"
            ? "No pending tasks. Great work!"
            : "No completed tasks yet."}
        </p>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Success state
  // ---------------------------------------------------------------------------
  return (
    <section aria-label="Task list">
      <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-400">
        {tasks.length} {tasks.length === 1 ? "task" : "tasks"}
        {filter !== "all" ? ` — ${filter}` : ""}
      </p>
      <ul className="space-y-3" role="list">
        {tasks.map((task) => (
          <li key={task.id}>
            <TaskCard
              task={task}
              userId={userId}
              onUpdate={handleTaskUpdate}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}
