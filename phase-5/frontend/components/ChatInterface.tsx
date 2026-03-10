"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import MessageList from "./MessageList";
import MessageInput, { MessageInputHandle } from "./MessageInput";
import ConversationList from "./ConversationList";
import {
  sendChatMessage,
  getConversations,
  getConversationMessages,
  deleteConversation,
  type Conversation,
  type Message as ApiMessage,
} from "@/lib/api";
import { logout, getUserDisplayName, getCurrentUser } from "@/lib/auth-utils";

interface Message {
  id: string | number;
  role: "user" | "assistant";
  content: string;
  tool_calls?: Array<{
    name: string;
    arguments: Record<string, unknown>;
  }> | null;
}

/**
 * ChatInterface component - main chat UI with conversation management.
 */
export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<MessageInputHandle>(null);

  // Close user menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Load conversations on mount and focus input
  useEffect(() => {
    loadConversations();
    // Auto-focus input on initial load (after login)
    setTimeout(() => messageInputRef.current?.focus(), 200);
  }, []);

  const loadConversations = async () => {
    try {
      const convs = await getConversations();
      setConversations(convs);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadConversationMessages = useCallback(async (conversationId: string) => {
    try {
      const msgs = await getConversationMessages(conversationId);
      setMessages(
        msgs.map((m: ApiMessage) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          tool_calls: m.tool_calls,
        }))
      );
    } catch (err) {
      console.error("Failed to load messages:", err);
      setError("Failed to load conversation messages");
    }
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadConversationMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId, loadConversationMessages]);

  const handleSendMessage = async (content: string) => {
    // Add optimistic user message
    const tempId = `temp-${Date.now()}`;
    const userMessage: Message = {
      id: tempId,
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(content, currentConversationId || undefined);

      // Update conversation ID if this was a new conversation
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        // Reload conversations to show the new one
        await loadConversations();
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.response,
        tool_calls: response.tool_calls,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      // Focus on input after response
      setTimeout(() => messageInputRef.current?.focus(), 100);
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempId));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
    setError(null);
  };

  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
    // Focus on input after new chat
    setTimeout(() => messageInputRef.current?.focus(), 100);
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      // Remove from local state
      setConversations((prev) => prev.filter((c) => c.id !== id));
      // Clear current conversation if it was deleted
      if (currentConversationId === id) {
        handleNewConversation();
      }
    } catch (err: unknown) {
      console.error("Failed to delete conversation:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to delete conversation";
      setError(errorMessage);
    }
  };

  const handleLogout = () => {
    logout(true);
  };

  const displayName = getUserDisplayName();
  const user = getCurrentUser();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-3 glass-button rounded-xl shadow-lg transition-all duration-300 hover:shadow-neon-purple"
      >
        <svg
          className="w-6 h-6 text-slate-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={sidebarOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
          />
        </svg>
      </button>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 fixed lg:relative inset-y-0 left-0 z-40 lg:z-0 transition-transform duration-300 ease-in-out`}
      >
        <ConversationList
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="glass border-b border-white/[0.07] px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3 pl-12 lg:pl-0">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/90 flex items-center justify-center shadow-neon-purple">
              <svg className="w-4.5 h-4.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-[15px] font-semibold gradient-text tracking-tight">
                FlowTask AI
              </h1>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                <p className="text-[11px] text-slate-500">AI agent ready</p>
              </div>
            </div>
          </div>

          {/* User profile dropdown */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-3 glass-button rounded-xl px-4 py-2 transition-all duration-300"
            >
              <div className="avatar avatar-user text-xs">
                {displayName.charAt(0).toUpperCase()}
              </div>
              <span className="hidden sm:block text-sm text-slate-300">{displayName}</span>
              <svg
                className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${userMenuOpen ? "rotate-180" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown menu */}
            {userMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 dropdown-glass animate-fade-in">
                <div className="p-4 border-b border-white/10">
                  <p className="text-sm font-medium text-white">{displayName}</p>
                  <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                </div>
                <div className="p-2">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-sm text-slate-300 hover:bg-white/5 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-auto">
          {/* Error banner */}
          {error && (
            <div className="mx-4 mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 animate-slide-up">
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="flex-1 text-sm text-red-400">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Messages */}
          <MessageList messages={messages} isLoading={isLoading} />
        </div>

        {/* Input - outside scroll container */}
        <MessageInput ref={messageInputRef} onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
