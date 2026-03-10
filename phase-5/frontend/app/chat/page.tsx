"use client";

import AuthGuard from "@/components/AuthGuard";
import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  return (
    <AuthGuard>
      <div className="h-screen overflow-hidden">
        <ChatInterface />
      </div>
    </AuthGuard>
  );
}
