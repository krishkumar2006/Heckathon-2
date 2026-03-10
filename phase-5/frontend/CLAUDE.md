# Frontend Guidelines - Phase 3 AI Chatbot

## Stack

- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- OpenAI ChatKit

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with auth
│   ├── page.tsx            # Landing/redirect
│   ├── chat/
│   │   └── page.tsx        # Chat interface with ChatKit
│   ├── auth/
│   │   ├── signin/page.tsx
│   │   └── signup/page.tsx
│   └── api/
│       └── auth/[...all]/route.ts  # Better Auth routes
├── components/
│   ├── ChatInterface.tsx   # ChatKit wrapper
│   ├── AuthGuard.tsx       # Protected route wrapper
│   └── ...
├── lib/
│   ├── api.ts              # Backend API client
│   ├── auth.ts             # Better Auth client
│   └── auth-client.ts      # Auth client instance
└── ...
```

## Patterns

- Use server components by default
- Client components only for interactivity (ChatKit, forms)
- API calls through `/lib/api.ts`
- Auth state managed via Better Auth client

## ChatKit Integration

```typescript
import { Chat } from '@openai/chatkit';

// ChatKit requires domain allowlist configuration
// See: https://platform.openai.com/settings/organization/security/domain-allowlist
```

## API Client

```typescript
// lib/api.ts
export async function sendMessage(message: string, conversationId?: string) {
  const token = await getAuthToken();
  return fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
}
```

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
BETTER_AUTH_SECRET=your-secret
```

## Running

```bash
npm install
npm run dev
```
