// frontend/app/chat/page.tsx
// Phase 3 — AI Chat Page
// "use client" — needs useState, useEffect, useRef, event handlers
// Auth guard: redirects to /login if no session
// Sends messages to POST /api/{userId}/chat with JWT attached

"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authClient } from "@/lib/auth-client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ToolCall {
  tool: string;
  result: Record<string, unknown>;
}

interface ChatMessage {
  role: "user" | "assistant" | "welcome";
  content: string;
  toolCalls?: ToolCall[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const WELCOME_MESSAGE: ChatMessage = {
  role: "welcome",
  content:
    "👋 Hi! I'm your AI assistant. I can help you manage tasks, view login activity, and get project stats. You can also ask me your email or name. What can I do for you today?",
};

const QUICK_ACTIONS = [
  { label: "📋 List Tasks",  fill: "Show all my tasks" },
  { label: "➕ Add Task",    fill: "I want to add a new task: " },
  { label: "📊 Stats",       fill: "Give me an overview of everything" },
  { label: "👤 My Profile",  fill: "What is my email and full name?" },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ToolBadge({ tool }: { tool: string }) {
  return (
    <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
      ✅ {tool}
    </span>
  );
}

function ThinkingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-2">
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "0ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "150ms" }}
      />
      <span
        className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
        style={{ animationDelay: "300ms" }}
      />
    </div>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  const isWelcome = msg.role === "welcome";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-2 text-sm text-white shadow-sm">
          {msg.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] space-y-1">
        <div
          className={`rounded-2xl rounded-tl-sm px-4 py-2 text-sm shadow-sm ${
            isWelcome
              ? "bg-indigo-50 text-indigo-900 border border-indigo-100"
              : "bg-gray-100 text-gray-900"
          }`}
        >
          <p className="whitespace-pre-wrap">{msg.content}</p>
        </div>
        {msg.toolCalls && msg.toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1 px-1">
            {msg.toolCalls.map((tc, i) => (
              <ToolBadge key={i} tool={tc.tool} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function ChatPage() {
  const router = useRouter();
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [userId, setUserId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auth guard
  useEffect(() => {
    async function checkAuth() {
      try {
        const sessionData = await authClient.getSession();
        const session = sessionData?.data;
        if (!session?.user?.id) {
          router.push("/login");
          return;
        }
        setUserId(session.user.id);

        // Get JWT token
        const tokenRes = await fetch("/api/token", {
          method: "GET",
          credentials: "include",
        });
        if (tokenRes.ok) {
          const tokenData = (await tokenRes.json()) as { token?: string };
          setToken(tokenData.token ?? null);
        }
      } catch {
        router.push("/login");
      }
    }
    checkAuth();
  }, [router]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading || !userId) return;
    if (!token) {
      setError("Session expired. Please log in again.");
      router.push("/login");
      return;
    }

    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/api/${userId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: text,
        }),
      });

      if (res.status === 401) {
        router.push("/login");
        return;
      }

      if (!res.ok) {
        const errData = (await res.json().catch(() => ({}))) as {
          detail?: string;
        };
        throw new Error(errData.detail ?? `Error ${res.status}`);
      }

      const data = (await res.json()) as {
        conversation_id: number;
        response: string;
        tool_calls: ToolCall[];
      };

      if (conversationId === null) {
        setConversationId(data.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          toolCalls: data.tool_calls,
        },
      ]);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Something went wrong. Try again.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ ${msg}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function handleQuickAction(fill: string) {
    setInput(fill);
    textareaRef.current?.focus();
  }

  if (!userId) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <p className="text-sm text-gray-500">Checking session…</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-4 py-3 shadow-sm">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg font-semibold text-gray-900">💬 AI Assistant</span>
            {conversationId && (
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                #{conversationId}
              </span>
            )}
          </div>
          <Link
            href="/dashboard"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← Dashboard
          </Link>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 py-4">
        <div className="mx-auto max-w-2xl space-y-3">
          {messages.map((msg, i) => (
            <MessageBubble key={i} msg={msg} />
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-tl-sm bg-gray-100 shadow-sm">
                <ThinkingDots />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input area */}
      <footer className="border-t border-gray-200 bg-white px-4 py-3">
        <div className="mx-auto max-w-2xl space-y-2">
          {/* Quick action buttons */}
          <div className="flex flex-wrap gap-1.5">
            {QUICK_ACTIONS.map((qa) => (
              <button
                key={qa.label}
                type="button"
                onClick={() => handleQuickAction(qa.fill)}
                className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
              >
                {qa.label}
              </button>
            ))}
          </div>

          {/* Error banner */}
          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
              {error}
            </p>
          )}

          {/* Textarea + send */}
          <div className="flex items-end gap-2">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
              rows={1}
              className="flex-1 resize-none rounded-xl border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
              style={{ maxHeight: "120px", overflowY: "auto" }}
              disabled={loading}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
              }}
            />
            <button
              type="button"
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Send message"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="h-4 w-4 rotate-90"
              >
                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
              </svg>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
