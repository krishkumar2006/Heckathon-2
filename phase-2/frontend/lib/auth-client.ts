// frontend/lib/auth-client.ts
// Client-safe — safe to import in client components and server components
// Required env vars: NEXT_PUBLIC_BETTER_AUTH_URL (optional, defaults to localhost:3000)
// NOTE: Uses "better-auth/react" (not "better-auth/client") so that useSession() is a
//       proper React hook rather than a nanostores Atom.

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL:
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL ?? "http://localhost:3000",
});
