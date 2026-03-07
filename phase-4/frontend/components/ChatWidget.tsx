"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
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
  timestamp?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const WELCOME: ChatMessage = {
  role: "welcome",
  content:
    "👋 Hey there! I'm your AI assistant.\n\nI can help you manage tasks, view login activity, and get project stats. You can also ask me your email or name. What can I do for you?",
  timestamp: now(),
};

const QUICK_ACTIONS = [
  { label: "📋 My Tasks",  fill: "Show all my tasks" },
  { label: "➕ Add Task",  fill: "I want to add a new task: " },
  { label: "📊 Overview",  fill: "Give me a full overview of everything" },
  { label: "👤 My Profile", fill: "What is my email and full name?" },
];

// ---------------------------------------------------------------------------
// Bot Avatar
// ---------------------------------------------------------------------------

function BotAvatar() {
  return (
    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-blue-500 shadow-sm text-xs">
      🤖
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tool Badges
// ---------------------------------------------------------------------------

function ToolBadge({ tool }: { tool: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
      {tool}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Typing indicator
// ---------------------------------------------------------------------------

function TypingBubble() {
  return (
    <div className="flex items-end gap-2">
      <BotAvatar />
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-white border border-gray-100 px-4 py-3 shadow-sm">
        <span
          className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce"
          style={{ animationDelay: "0ms", animationDuration: "1s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce"
          style={{ animationDelay: "200ms", animationDuration: "1s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce"
          style={{ animationDelay: "400ms", animationDuration: "1s" }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Message Bubble
// ---------------------------------------------------------------------------

function Bubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";

  if (isUser) {
    return (
      <div className="flex flex-col items-end gap-1">
        <div className="max-w-[78%] rounded-2xl rounded-br-sm bg-gradient-to-br from-indigo-600 to-blue-500 px-4 py-2.5 shadow-md">
          <p className="text-[13px] leading-relaxed text-white whitespace-pre-wrap">
            {msg.content}
          </p>
        </div>
        {msg.timestamp && (
          <span className="px-1 text-[10px] text-gray-400">{msg.timestamp}</span>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <div className="flex items-end gap-2 max-w-[85%]">
        <BotAvatar />
        <div className="space-y-1.5">
          <div className="rounded-2xl rounded-bl-sm bg-white border border-gray-100 px-4 py-2.5 shadow-sm">
            <p className="text-[13px] leading-relaxed text-gray-800 whitespace-pre-wrap">
              {msg.content}
            </p>
          </div>
          {msg.toolCalls && msg.toolCalls.length > 0 && (
            <div className="flex flex-wrap gap-1 pl-1">
              {msg.toolCalls.map((tc, i) => (
                <ToolBadge key={i} tool={tc.tool} />
              ))}
            </div>
          )}
        </div>
      </div>
      {msg.timestamp && (
        <span className="pl-9 text-[10px] text-gray-400">{msg.timestamp}</span>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main widget
// ---------------------------------------------------------------------------

export default function ChatWidget() {
  const router = useRouter();
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [open, setOpen] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [unread, setUnread] = useState(0);

  // Auth — fetch user + token once on mount
  useEffect(() => {
    async function init() {
      try {
        const sessionData = await authClient.getSession();
        const session = sessionData?.data;
        if (!session?.user?.id) return;
        setUserId(session.user.id);
        const res = await fetch("/api/token", { credentials: "include" });
        if (res.ok) {
          const data = (await res.json()) as { token?: string };
          setToken(data.token ?? null);
        }
      } catch {
        // silently ignore
      }
    }
    init();
  }, [router]);

  // Auto-scroll
  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, open]);

  // Focus textarea when opened
  useEffect(() => {
    if (open) {
      setUnread(0);
      setTimeout(() => textareaRef.current?.focus(), 80);
    }
  }, [open]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading || !userId || !token) return;

    setInput("");
    setError(null);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, timestamp: now() },
    ]);
    setLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/api/${userId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ conversation_id: conversationId, message: text }),
      });

      if (res.status === 401) { router.push("/login"); return; }

      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(err.detail ?? `Error ${res.status}`);
      }

      const data = (await res.json()) as {
        conversation_id: number;
        response: string;
        tool_calls: ToolCall[];
      };

      if (conversationId === null) setConversationId(data.conversation_id);

      const newMsg: ChatMessage = {
        role: "assistant",
        content: data.response,
        toolCalls: data.tool_calls,
        timestamp: now(),
      };

      setMessages((prev) => [...prev, newMsg]);
      if (!open) setUnread((n) => n + 1);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `❌ ${msg}`, timestamp: now() },
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

  if (!userId) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">

      {/* ------------------------------------------------------------------ */}
      {/* Chat panel                                                           */}
      {/* ------------------------------------------------------------------ */}
      <div
        className="flex w-[360px] flex-col overflow-hidden rounded-2xl bg-gray-50 shadow-[0_24px_64px_rgba(0,0,0,0.18)]"
        style={{
          height: "520px",
          border: "1px solid rgba(0,0,0,0.08)",
          transformOrigin: "bottom right",
          transition: "opacity 0.2s ease, transform 0.2s ease",
          opacity: open ? 1 : 0,
          transform: open ? "scale(1) translateY(0)" : "scale(0.92) translateY(16px)",
          pointerEvents: open ? "auto" : "none",
        }}
      >
        {/* Header */}
        <div className="relative flex items-center gap-3 bg-gradient-to-r from-indigo-600 via-indigo-500 to-blue-500 px-4 py-3.5">
          {/* Bot avatar with glow ring */}
          <div className="relative">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/20 text-lg shadow-inner backdrop-blur-sm">
              🤖
            </div>
            <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-indigo-500 bg-emerald-400" />
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-white leading-none">AI Assistant</p>
            <p className="mt-0.5 text-[11px] text-indigo-200">Online · Powered by Groq</p>
          </div>

          {/* Close button */}
          <button
            onClick={() => setOpen(false)}
            className="flex h-7 w-7 items-center justify-center rounded-full text-indigo-200 transition-colors hover:bg-white/20 hover:text-white"
            aria-label="Close"
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scroll-smooth"
          style={{ background: "linear-gradient(180deg, #f8faff 0%, #f1f4fb 100%)" }}>
          {messages.map((msg, i) => (
            <Bubble key={i} msg={msg} />
          ))}
          {loading && <TypingBubble />}
          <div ref={bottomRef} />
        </div>

        {/* Quick actions */}
        <div className="border-t border-gray-100 bg-white px-4 pt-3 pb-0">
          <div className="flex flex-wrap gap-1.5">
            {QUICK_ACTIONS.map((qa) => (
              <button
                key={qa.label}
                type="button"
                onClick={() => { setInput(qa.fill); textareaRef.current?.focus(); }}
                className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-[11px] font-medium text-gray-600 transition-all hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 hover:shadow-sm"
              >
                {qa.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-white px-4 pt-2">
            <p className="rounded-xl bg-red-50 border border-red-100 px-3 py-1.5 text-[11px] text-red-600">
              {error}
            </p>
          </div>
        )}

        {/* Input */}
        <div className="bg-white px-4 py-3">
          <div className="flex items-end gap-2 rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2 focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything…"
              rows={1}
              disabled={loading}
              className="flex-1 resize-none bg-transparent text-[13px] text-gray-800 placeholder-gray-400 focus:outline-none disabled:opacity-50 leading-relaxed"
              style={{ maxHeight: "80px", overflowY: "auto" }}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${Math.min(el.scrollHeight, 80)}px`;
              }}
            />
            <button
              type="button"
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              aria-label="Send message"
              className="mb-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-blue-500 text-white shadow-md transition-all hover:shadow-lg hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40 disabled:scale-100 disabled:shadow-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-3.5 w-3.5">
                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
              </svg>
            </button>
          </div>
          <p className="mt-1.5 text-center text-[10px] text-gray-300">
            Enter to send · Shift+Enter for newline
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Toggle FAB                                                           */}
      {/* ------------------------------------------------------------------ */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close chat" : "Open AI Assistant"}
        className="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-indigo-600 to-blue-500 shadow-[0_8px_24px_rgba(99,102,241,0.5)] transition-all hover:shadow-[0_12px_32px_rgba(99,102,241,0.6)] hover:scale-110 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        style={{ transition: "all 0.2s ease" }}
      >
        {/* Unread badge */}
        {!open && unread > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-md">
            {unread}
          </span>
        )}

        {/* Icon */}
        <span
          style={{
            transition: "opacity 0.15s ease, transform 0.15s ease",
            opacity: open ? 0 : 1,
            transform: open ? "rotate(90deg) scale(0.5)" : "rotate(0deg) scale(1)",
            position: "absolute",
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0112 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 01-3.476.383.39.39 0 00-.297.17l-2.755 4.133a.75.75 0 01-1.248 0l-2.755-4.133a.39.39 0 00-.297-.17 48.9 48.9 0 01-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97z" clipRule="evenodd" />
          </svg>
        </span>

        <span
          style={{
            transition: "opacity 0.15s ease, transform 0.15s ease",
            opacity: open ? 1 : 0,
            transform: open ? "rotate(0deg) scale(1)" : "rotate(-90deg) scale(0.5)",
            position: "absolute",
          }}
        >
          <svg className="h-6 w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </span>
      </button>
    </div>
  );
}
