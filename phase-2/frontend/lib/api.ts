// frontend/lib/api.ts
// Centralized API client — ALL backend calls go through here
// Required env vars: NEXT_PUBLIC_API_URL
// Do NOT call fetch() directly in components — use these functions instead

import { authClient } from "@/lib/auth-client";
import type {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
} from "@/types/task";

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------

/**
 * Calls /api/token (our custom Next.js route) which reads the session
 * server-side and returns a signed HS256 JWT for the FastAPI backend.
 */
async function getJwtToken(): Promise<string | null> {
  try {
    const tokenRes = await fetch("/api/token", {
      method: "GET",
      credentials: "include",
    });
    if (!tokenRes.ok) return null;
    const tokenData = (await tokenRes.json()) as { token?: string };
    return tokenData.token ?? null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Base fetch with auth
// ---------------------------------------------------------------------------

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Wraps fetch with JWT Authorization header.
 * Throws typed errors for common HTTP error codes.
 */
async function fetchWithAuth(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getJwtToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }
  if (response.status === 403) {
    throw new Error("Access denied");
  }
  if (response.status === 404) {
    throw new Error("Task not found");
  }
  if (response.status >= 500) {
    throw new Error("Server error, try again");
  }

  return response;
}

// ---------------------------------------------------------------------------
// Task API functions
// ---------------------------------------------------------------------------

/**
 * Fetch all tasks for a user, optionally filtered by status.
 * GET /api/{userId}/tasks?task_status={status}
 */
export async function getTasks(
  userId: string,
  status?: "all" | "pending" | "completed"
): Promise<Task[]> {
  const query =
    status && status !== "all"
      ? `?task_status=${encodeURIComponent(status)}`
      : "";
  const response = await fetchWithAuth(`/api/${userId}/tasks${query}`);
  return response.json() as Promise<Task[]>;
}

/**
 * Create a new task for a user.
 * POST /api/{userId}/tasks
 */
export async function createTask(
  userId: string,
  data: CreateTaskInput
): Promise<Task> {
  const response = await fetchWithAuth(`/api/${userId}/tasks`, {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json() as Promise<Task>;
}

/**
 * Fetch a single task by ID.
 * GET /api/{userId}/tasks/{taskId}
 */
export async function getTask(userId: string, taskId: number): Promise<Task> {
  const response = await fetchWithAuth(`/api/${userId}/tasks/${taskId}`);
  return response.json() as Promise<Task>;
}

/**
 * Update a task's fields (partial update).
 * PUT /api/{userId}/tasks/{taskId}
 */
export async function updateTask(
  userId: string,
  taskId: number,
  data: UpdateTaskInput
): Promise<Task> {
  const response = await fetchWithAuth(`/api/${userId}/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return response.json() as Promise<Task>;
}

/**
 * Delete a task by ID.
 * DELETE /api/{userId}/tasks/{taskId}
 */
export async function deleteTask(
  userId: string,
  taskId: number
): Promise<void> {
  await fetchWithAuth(`/api/${userId}/tasks/${taskId}`, {
    method: "DELETE",
  });
}

/**
 * Toggle a task's completed status.
 * PATCH /api/{userId}/tasks/{taskId}/complete
 */
export async function toggleComplete(
  userId: string,
  taskId: number
): Promise<Task> {
  const response = await fetchWithAuth(
    `/api/${userId}/tasks/${taskId}/complete`,
    {
      method: "PATCH",
    }
  );
  return response.json() as Promise<Task>;
}
