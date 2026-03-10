"use client";

import { useEffect, useRef } from "react";

interface Message {
  id: string | number;
  role: "user" | "assistant";
  content: string;
  tool_calls?: Array<{
    name: string;
    arguments: Record<string, unknown>;
  }> | null;
}

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading = false }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-center max-w-sm animate-fade-in">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center mb-5">
            <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>

          <h3 className="text-base font-semibold text-slate-200 mb-1">
            What would you like to do?
          </h3>
          <p className="text-sm text-slate-500 mb-6">
            Talk to your AI agent and manage tasks naturally.
          </p>

          <div className="space-y-2 text-left">
            {[
              { color: "bg-indigo-500", text: "\"Add a high priority task for tomorrow\"" },
              { color: "bg-amber-500", text: "\"Show all my pending tasks\"" },
              { color: "bg-sky-500", text: "\"Search tasks about the project\"" },
              { color: "bg-rose-500", text: "\"Complete task 3 and delete task 5\"" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${item.color}`}></span>
                <span className="text-xs text-slate-400">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-5 space-y-5">
      {messages.map((message, index) => (
        <div
          key={message.id}
          className={`flex items-end gap-2.5 animate-slide-up ${
            message.role === "user" ? "flex-row-reverse" : "flex-row"
          }`}
          style={{ animationDelay: `${Math.min(index * 0.04, 0.25)}s` }}
        >
          {/* Avatar */}
          <div className={`flex-shrink-0 ${
            message.role === "user" ? "avatar avatar-user" : "avatar avatar-assistant"
          }`}>
            {message.role === "user" ? (
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            )}
          </div>

          {/* Bubble */}
          <div className={`max-w-[72%] px-4 py-2.5 ${
            message.role === "user" ? "bubble-user" : "bubble-assistant"
          }`}>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-2 pt-2 border-t border-white/10">
                <div className="flex items-center gap-1.5 text-[11px] text-indigo-300/80">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M4 6h16M4 10h16M4 14h8" />
                  </svg>
                  <span>{message.tool_calls.map((tc) => tc.name).join(", ")}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Typing indicator */}
      {isLoading && (
        <div className="flex items-end gap-2.5 animate-fade-in">
          <div className="avatar avatar-assistant">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="bubble-assistant px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
              <span className="text-xs text-slate-500">thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
