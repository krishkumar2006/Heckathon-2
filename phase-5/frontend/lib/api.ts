/**
 * API client for communicating with the Todo Chatbot backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls: Array<{
    name: string;
    arguments: Record<string, unknown>;
  }>;
}

interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  tool_calls: Array<{
    name: string;
    arguments: Record<string, unknown>;
  }> | null;
  created_at: string;
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Get the JWT token from Better Auth session.
 * This should be replaced with actual Better Auth token retrieval.
 */
async function getAuthToken(): Promise<string | null> {
  // In a real implementation, this would get the token from Better Auth
  // For now, we'll check for a token in localStorage or cookies
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token");
  }
  return null;
}

/**
 * Make an authenticated API request.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Redirect to login on auth failure - but only if not already on signin page
    if (typeof window !== "undefined") {
      const currentPath = window.location.pathname;
      // Prevent redirect loop - only redirect if NOT on auth pages
      if (!currentPath.startsWith("/signin") && !currentPath.startsWith("/signup")) {
        // Clear invalid token before redirect
        localStorage.removeItem("auth_token");
        window.location.href = "/signin";
      }
    }
    throw new ApiError(401, "Unauthorized");
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorData.detail || "An error occurred"
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/**
 * Send a chat message and receive AI response.
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
}

/**
 * Get all conversations for the current user.
 */
export async function getConversations(): Promise<Conversation[]> {
  return apiRequest<Conversation[]>("/api/chat/conversations");
}

/**
 * Get a single conversation by ID.
 */
export async function getConversation(
  conversationId: string
): Promise<Conversation> {
  return apiRequest<Conversation>(`/api/chat/conversations/${conversationId}`);
}

/**
 * Get all messages for a conversation.
 */
export async function getConversationMessages(
  conversationId: string
): Promise<Message[]> {
  return apiRequest<Message[]>(
    `/api/chat/conversations/${conversationId}/messages`
  );
}

/**
 * Delete a conversation and all its messages.
 */
export async function deleteConversation(conversationId: string): Promise<void> {
  await apiRequest<void>(`/api/chat/conversations/${conversationId}`, {
    method: "DELETE",
  });
}

/**
 * Set the auth token (for use after login).
 */
export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

/**
 * Clear the auth token (for use after logout).
 */
export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

// --- Task API ---

interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: string;
  due_date: string | null;
  reminder_offset_minutes: number | null;
  recurrence: string;
  is_recurring: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

interface GetTasksParams {
  search?: string;
  priority?: "high" | "medium" | "low";
  tag?: string;
  status?: "all" | "pending" | "completed";
  sort?: "due_date" | "priority" | "title" | "created_at";
  order?: "asc" | "desc";
  due_from?: string;
  due_to?: string;
}

export async function getTasks(
  userId: string,
  params: GetTasksParams = {}
): Promise<Task[]> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) query.set(key, value);
  }
  const qs = query.toString();
  return apiRequest<Task[]>(`/api/${userId}/tasks${qs ? `?${qs}` : ""}`);
}

export async function createTask(
  userId: string,
  data: {
    title: string;
    description?: string;
    priority?: string;
    due_date?: string;
    reminder_offset_minutes?: number;
    recurrence?: string;
  }
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTask(
  userId: string,
  taskId: number,
  data: {
    title?: string;
    description?: string;
    priority?: string;
    due_date?: string;
    reminder_offset_minutes?: number;
    recurrence?: string;
  }
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteTask(
  userId: string,
  taskId: number
): Promise<void> {
  await apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
    method: "DELETE",
  });
}

export async function addTaskTags(
  userId: string,
  taskId: number,
  tags: string[]
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/tags`, {
    method: "POST",
    body: JSON.stringify({ tags }),
  });
}

export async function removeTaskTag(
  userId: string,
  taskId: number,
  tag: string
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/tags/${tag}`, {
    method: "DELETE",
  });
}

export { ApiError };
export type { ChatResponse, Conversation, Message, Task, GetTasksParams };
