"use client";

import { useState, KeyboardEvent, useRef, useImperativeHandle, forwardRef } from "react";

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export interface MessageInputHandle {
  focus: () => void;
}

const MessageInput = forwardRef<MessageInputHandle, MessageInputProps>(function MessageInput({
  onSendMessage,
  disabled = false,
  placeholder = "Ask your AI agent anything... (e.g. 'Add task: submit report by Friday')",
}, ref) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => { textareaRef.current?.focus(); }
  }));

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSendMessage(trimmed);
      setMessage("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const hasText = message.trim().length > 0;

  return (
    <div className="flex-shrink-0 border-t border-white/[0.06] bg-[rgba(10,10,20,0.6)] backdrop-blur-xl px-4 py-3">
      <div className="flex items-end gap-2.5 max-w-4xl mx-auto">
        {/* Input area */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full resize-none input-glass rounded-2xl px-4 py-3 text-sm disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ minHeight: "46px", maxHeight: "120px" }}
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSubmit}
          disabled={disabled || !hasText}
          className={`flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 ${
            hasText && !disabled
              ? "bg-indigo-600 hover:bg-indigo-500 shadow-neon-purple hover:scale-105 active:scale-95"
              : "bg-white/5 border border-white/10 cursor-not-allowed opacity-40"
          }`}
        >
          {disabled ? (
            <svg className="w-4 h-4 text-indigo-300 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-4 h-4 text-white translate-x-[1px]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>

      <p className="text-center text-[10px] text-slate-700 mt-2">
        Press <kbd className="px-1 py-0.5 rounded bg-white/5 text-slate-600 text-[9px]">Enter</kbd> to send · <kbd className="px-1 py-0.5 rounded bg-white/5 text-slate-600 text-[9px]">Shift+Enter</kbd> for new line
      </p>
    </div>
  );
});

export default MessageInput;
