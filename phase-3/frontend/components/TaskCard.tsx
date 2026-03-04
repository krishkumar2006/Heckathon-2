// frontend/components/TaskCard.tsx
// Client Component — single task card with toggle, inline edit, and delete
// Acceptance checks: three view modes (normal, editing, confirm-delete), loading/error states on every async op

"use client";

import { useState } from "react";
import type { Task } from "@/types/task";
import * as api from "@/lib/api";

interface TaskCardProps {
  task: Task;
  userId: string;
  onUpdate: () => void;
}

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function TaskCard({ task, userId, onUpdate }: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(
    task.description ?? ""
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Toggle completion
  // ---------------------------------------------------------------------------
  async function handleToggle() {
    setError(null);
    setLoading(true);
    try {
      await api.toggleComplete(userId, task.id);
      onUpdate();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to update task.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Enter edit mode
  // ---------------------------------------------------------------------------
  function handleEditStart() {
    setEditTitle(task.title);
    setEditDescription(task.description ?? "");
    setError(null);
    setIsEditing(true);
  }

  // ---------------------------------------------------------------------------
  // Save edit
  // ---------------------------------------------------------------------------
  async function handleSave() {
    setError(null);
    const trimmedTitle = editTitle.trim();
    if (!trimmedTitle) {
      setError("Task title cannot be empty.");
      return;
    }
    setLoading(true);
    try {
      await api.updateTask(userId, task.id, {
        title: trimmedTitle,
        description: editDescription.trim() || undefined,
      });
      onUpdate();
      setIsEditing(false);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to save task.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Delete
  // ---------------------------------------------------------------------------
  async function handleDelete() {
    setError(null);
    setLoading(true);
    try {
      await api.deleteTask(userId, task.id);
      onUpdate();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to delete task.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Render: Delete confirmation view
  // ---------------------------------------------------------------------------
  if (showConfirm) {
    return (
      <article
        className="rounded-xl border border-red-200 bg-red-50 p-4 sm:p-5"
        aria-label="Delete confirmation"
      >
        <p className="text-sm font-medium text-red-800">
          Are you sure you want to delete this task?
        </p>
        <p className="mt-1 text-sm text-red-600 line-clamp-1">{task.title}</p>

        {error && (
          <div
            role="alert"
            aria-live="assertive"
            className="mt-3 rounded-lg bg-white px-3 py-2 text-sm text-red-700 border border-red-200"
          >
            {error}
          </div>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={handleDelete}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && (
              <svg
                className="h-3.5 w-3.5 animate-spin"
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
            {loading ? "Deleting..." : "Confirm Delete"}
          </button>
          <button
            onClick={() => {
              setShowConfirm(false);
              setError(null);
            }}
            disabled={loading}
            className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:opacity-60"
          >
            Cancel
          </button>
        </div>
      </article>
    );
  }

  // ---------------------------------------------------------------------------
  // Render: Edit form view
  // ---------------------------------------------------------------------------
  if (isEditing) {
    return (
      <article
        className="rounded-xl border border-blue-200 bg-white p-4 shadow-sm sm:p-5"
        aria-label="Edit task"
      >
        <div className="space-y-3">
          <div>
            <label
              htmlFor={`edit-title-${task.id}`}
              className="block text-sm font-medium text-gray-700"
            >
              Title <span aria-hidden="true" className="text-red-500">*</span>
            </label>
            <input
              id={`edit-title-${task.id}`}
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              maxLength={200}
              disabled={loading}
              aria-describedby={
                error ? `edit-error-${task.id}` : undefined
              }
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
            />
          </div>

          <div>
            <label
              htmlFor={`edit-description-${task.id}`}
              className="block text-sm font-medium text-gray-700"
            >
              Description{" "}
              <span className="text-xs font-normal text-gray-400">
                (optional)
              </span>
            </label>
            <textarea
              id={`edit-description-${task.id}`}
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              maxLength={1000}
              rows={2}
              disabled={loading}
              className="mt-1 block w-full resize-y rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
            />
          </div>

          {error && (
            <div
              id={`edit-error-${task.id}`}
              role="alert"
              aria-live="assertive"
              className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleSave}
              disabled={loading}
              className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading && (
                <svg
                  className="h-3.5 w-3.5 animate-spin"
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
              {loading ? "Saving..." : "Save"}
            </button>
            <button
              onClick={() => {
                setIsEditing(false);
                setError(null);
              }}
              disabled={loading}
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:opacity-60"
            >
              Cancel
            </button>
          </div>
        </div>
      </article>
    );
  }

  // ---------------------------------------------------------------------------
  // Render: Normal view
  // ---------------------------------------------------------------------------
  return (
    <article
      className="flex gap-3 rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-colors hover:border-gray-300 sm:gap-4 sm:p-5"
      aria-label={`Task: ${task.title}`}
    >
      {/* Checkbox */}
      <div className="mt-0.5 flex-shrink-0">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          disabled={loading}
          aria-label={
            task.completed ? "Mark as incomplete" : "Mark as complete"
          }
          className="h-4 w-4 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm font-medium leading-snug ${
            task.completed
              ? "text-gray-400 line-through"
              : "text-gray-900"
          }`}
        >
          {task.title}
        </p>

        {task.description && (
          <p className="mt-1 text-sm text-gray-500">{task.description}</p>
        )}

        <p className="mt-1.5 text-xs text-gray-400">
          {formatDate(task.created_at)}
        </p>

        {error && (
          <div
            role="alert"
            aria-live="assertive"
            className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700"
          >
            {error}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-shrink-0 items-start gap-1.5">
        <button
          onClick={handleEditStart}
          disabled={loading}
          aria-label="Edit task"
          className="rounded-md px-2 py-1 text-xs font-medium text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400 disabled:opacity-60"
        >
          Edit
        </button>
        <button
          onClick={() => {
            setShowConfirm(true);
            setError(null);
          }}
          disabled={loading}
          aria-label="Delete task"
          className="rounded-md px-2 py-1 text-xs font-medium text-red-500 transition-colors hover:bg-red-50 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:opacity-60"
        >
          Delete
        </button>
      </div>
    </article>
  );
}
