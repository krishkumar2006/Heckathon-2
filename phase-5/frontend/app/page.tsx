import Link from "next/link";

export default function Home() {
  return (
    <div className="h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated floating background orbs */}
      <div className="orb orb-purple w-[400px] h-[400px] -top-20 -left-20" style={{ animationDelay: "0s" }}></div>
      <div className="orb orb-pink w-[300px] h-[300px] top-1/3 -right-20" style={{ animationDelay: "2s" }}></div>
      <div className="orb orb-cyan w-[250px] h-[250px] bottom-10 left-1/4" style={{ animationDelay: "4s" }}></div>

      {/* Content */}
      <div className="relative z-10 text-center px-4">
        {/* Glowing badge */}
        <div className="inline-flex items-center gap-2 badge-glow mb-8 animate-fade-in">
          <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></span>
          AI-Powered Task Management
        </div>

        {/* Main heading */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
          <span className="gradient-text-animated">AI Todo</span>
          <br />
          <span className="text-white">Chatbot</span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-slate-400 mb-10 max-w-xl mx-auto animate-slide-up" style={{ animationDelay: "0.1s" }}>
          Manage your tasks using natural language.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: "0.2s" }}>
          <Link
            href="/signin"
            className="btn-neon px-8 py-4 text-lg rounded-xl inline-flex items-center gap-2"
          >
            Sign in
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
          <Link
            href="/signup"
            className="btn-neon-outline px-8 py-4 text-lg rounded-xl"
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
