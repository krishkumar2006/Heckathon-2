// frontend/components/TaskForm.tsx
// Client Component — create new task form
// Acceptance checks: validates title, shows loading/error, calls onTaskCreated on success

"use client";

import { useState } from "react";
import * as api from "@/lib/api";

interface TaskFormProps {
  userId: string;
  onTaskCreated: () => void;
}

export default function TaskForm({ userId, onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    // Acceptance check: title must not be empty
    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setError("Task title is required.");
      return;
    }

    setLoading(true);
    try {
      await api.createTask(userId, {
        title: trimmedTitle,
        description: description.trim() || undefined,
      });
      // Acceptance check: clear form on success
      setTitle("");
      setDescription("");
      onTaskCreated();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to create task.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      aria-labelledby="task-form-heading"
      className="mb-8 rounded-xl border border-gray-200 bg-white p-5 shadow-sm sm:p-6"
    >
      <h2
        id="task-form-heading"
        className="mb-4 text-base font-semibold text-gray-900"
      >
        Add a new task
      </h2>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {/* Title field */}
        <div>
          <div className="flex items-baseline justify-between">
            <label
              htmlFor="task-title"
              className="block text-sm font-medium text-gray-700"
            >
              Title <span aria-hidden="true" className="text-red-500">*</span>
            </label>
            <span
              className="text-xs text-gray-400"
              aria-live="polite"
              aria-atomic="true"
            >
              {title.length}/200
            </span>
          </div>
          <input
            id="task-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            placeholder="What needs to be done?"
            required
            disabled={loading}
            aria-required="true"
            aria-describedby={error ? "task-form-error" : undefined}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        {/* Description field */}
        <div>
          <div className="flex items-baseline justify-between">
            <label
              htmlFor="task-description"
              className="block text-sm font-medium text-gray-700"
            >
              Description{" "}
              <span className="text-xs font-normal text-gray-400">
                (optional)
              </span>
            </label>
            <span
              className="text-xs text-gray-400"
              aria-live="polite"
              aria-atomic="true"
            >
              {description.length}/1000
            </span>
          </div>
          <textarea
            id="task-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={1000}
            rows={3}
            placeholder="Add details about this task..."
            disabled={loading}
            className="mt-1 block w-full resize-y rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        {/* Error message */}
        {error && (
          <div
            id="task-form-error"
            role="alert"
            aria-live="assertive"
            className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {/* Submit button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && (
              // Acceptance check: spinner shown during loading
              <svg
                className="h-4 w-4 animate-spin"
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
            )}
            {loading ? "Adding..." : "Add task"}
          </button>
        </div>
      </form>
    </section>
  );
}
