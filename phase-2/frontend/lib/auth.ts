// frontend/lib/auth.ts
// Server-only — DO NOT import in client components

import { betterAuth } from "better-auth";
import { Pool } from "@neondatabase/serverless";

if (!process.env.DATABASE_URL) {
  throw new Error("Missing required environment variable: DATABASE_URL");
}
if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error("Missing required environment variable: BETTER_AUTH_SECRET");
}

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  secret: process.env.BETTER_AUTH_SECRET,
  emailAndPassword: {
    enabled: true,
  },
});
