// frontend/app/api/auth/[...all]/route.ts
// Better Auth catch-all API route handler
// Handles: POST /api/auth/sign-in, POST /api/auth/sign-up, GET /api/auth/session, etc.

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
