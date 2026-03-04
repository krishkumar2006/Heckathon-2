# Research: Phase 3 — AI Chat Assistant

**Feature**: `002-phase3-ai-chat`
**Date**: 2026-03-01
**Status**: Complete — all decisions resolved

---

## Decision 1: AI Provider

**Decision**: Use Groq API (`llama-3.3-70b-versatile`)
**Rationale**:
- Free tier at console.groq.com — no credit card required
- Supports OpenAI-compatible `tool_calls` format
- Fast inference (low latency for hackathon demo)
- `llama-3.3-70b-versatile` is the recommended model for function calling

**Alternatives Considered**:
- OpenAI GPT-4 — rejected (paid, violates Constitution Law XII)
- Anthropic Claude API — rejected (paid, violates Constitution Law XII)
- Local Ollama — rejected (too slow on free tier infra, setup complexity)

**Configuration**:
```python
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=full_messages,
    tools=GROQ_TOOLS,
    tool_choice="auto",
    max_tokens=1000
)
```

---

## Decision 2: Tool Protocol (MCP SDK)

**Decision**: Use `mcp==1.0.0` (official MCP SDK) as the tool abstraction layer
**Rationale**:
- Official SDK from Anthropic — well-documented
- Free (`pip install mcp`)
- Stateless by design — matches Constitution Law XVII
- No server needed for hackathon; tools run in-process

**Pattern Used**: MCP tools as plain Python functions (no MCP server transport).
The `mcp_server.py` module exposes functions directly called by `execute_tool()`.
The MCP SDK is imported to satisfy the package requirement and for future extensibility.

**Alternatives Considered**:
- Custom tool dispatcher — rejected (reinvents the wheel)
- LangChain tools — rejected (heavy dependency, paid features)

---

## Decision 3: Login Activity Tracking

**Decision**: HTTP middleware in `backend/main.py` (additive only)
**Rationale**:
- FastAPI `@app.middleware("http")` is purely additive — no existing code touched
- Fires on every request; filters by URL pattern (`/api/auth/sign-in`) + status code (200)
- Captures IP from `request.client.host` and device from `User-Agent` header

**Challenge**: Extracting `user_id` from the sign-in response.
The sign-in response body is consumed by `call_next(request)`. To extract user_id:
- The Better Auth `sign-in` endpoint returns a JSON body with `user.id`.
- We need to buffer the response body to parse it.
- Pattern: use `response.body` after calling `call_next(request)`.

**Implementation note**: Response body buffering requires wrapping with a custom
`Response` object since streaming responses cannot be read twice. Use:
```python
import json
from starlette.responses import Response

response = await call_next(request)
body = b""
async for chunk in response.body_iterator:
    body += chunk

# Parse user_id from body if sign-in
if "/api/auth/sign-in" in str(request.url) and response.status_code == 200:
    try:
        data = json.loads(body)
        user_id = data.get("user", {}).get("id") or data.get("userId")
        # save activity...
    except Exception:
        pass

return Response(
    content=body,
    status_code=response.status_code,
    headers=dict(response.headers),
    media_type=response.media_type,
)
```

---

## Decision 4: User-Agent Parsing

**Decision**: `user-agents==2.2.0` library
**Rationale**:
- Simple API: `ua = parse(ua_string)` → `ua.browser.family + " on " + ua.os.family`
- Returns "Other" for unknown browsers/OS — safe for edge cases
- Free, lightweight

**Format**: `"Chrome on Windows"`, `"Safari on macOS"`, `"Unknown on Unknown"`

```python
from user_agents import parse as parse_ua

def parse_device(ua_string: str) -> str:
    try:
        ua = parse_ua(ua_string)
        browser = ua.browser.family or "Unknown"
        os_name = ua.os.family or "Unknown"
        return f"{browser} on {os_name}"
    except Exception:
        return "Unknown device"
```

---

## Decision 5: Date Formatting

**Decision**: `python-dateutil==2.9.0` with `datetime.utcnow()`
**Rationale**:
- Human-readable format for AI responses: `"Sunday, March 1, 2026"`
- Activity timestamps: `"Sunday, March 1 at 10:30 AM"`
- `dateutil` provides `parser` and formatting utilities

**Format strings**:
```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
date_str = now.strftime("%A, %B %-d, %Y")        # "Sunday, March 1, 2026"
time_str = now.strftime("%-I:%M %p UTC")          # "10:30 AM UTC"
activity_str = now.strftime("%A, %B %-d at %-I:%M %p")  # "Sunday, March 1 at 10:30 AM"
```

Note: On Windows use `%#d` and `%#I` (not `%-d` and `%-I`). For cross-platform:
```python
day = str(now.day)      # no leading zero
hour = str(now.hour % 12 or 12)  # 12-hour no leading zero
```

---

## Decision 6: Conversation History Strategy

**Decision**: Full history loaded from DB on every request (stateless)
**Rationale**:
- Matches Constitution Law XIV (Stateless Server)
- Messages stored as `role`/`content` pairs in `messages` table
- Load all messages for conversation ordered by `created_at ASC`
- Pass to Groq as the message history (excluding tool_calls_json for agent input)

**Multi-turn context**: History grows with each message. For hackathon scale
(~10-20 messages per session), this is fine. At scale, a sliding window would be needed.

**Tool calls in history**: The `tool_calls_json` field stores what tools were called
for the assistant message. It is NOT passed back into Groq history (only role/content).

---

## Decision 7: Frontend Auth Pattern

**Decision**: Use `authClient.getSession()` directly in chat page
**Rationale**:
- The chat page is a `"use client"` component (needs state)
- `authClient` is already available from `@/lib/auth-client`
- Pattern: `session?.data?.token` for JWT
- Same guard as dashboard: if no session → `router.push("/login")`

**Note**: The spec says the chat page should NOT go through `frontend/lib/api.ts`
(which is a frozen file). Instead, the chat page makes direct `fetch()` calls with
the token attached. This is the one exception to RULE 4 since api.ts is frozen
and cannot be modified (RULE 4 applies to NEW non-frozen components — the chat
page is a NEW component, but modifying api.ts would violate the frozen file rule).

**Resolution**: The chat `sendMessage()` function makes a direct `fetch()` call
to `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat` with JWT attached.
This is explicitly documented as the intended pattern in the spec (FR-024).

---

## Decision 8: Quick Action Buttons

**Decision**: Pre-fill input text (no auto-send)
**Rationale**:
- User should be able to review/edit the pre-filled text before sending
- Avoids accidental API calls
- Spec FR-023 explicitly says: "4 quick action buttons pre-filling input (not auto-sending)"

**4 buttons**:
1. `📋 List Tasks` → pre-fills "Show all my tasks"
2. `➕ Add Task` → pre-fills "I want to add a new task: "
3. `📧 Emails` → pre-fills "Show my recent emails"
4. `📊 Stats` → pre-fills "Give me an overview of everything"

---

## Resolved: All NEEDS CLARIFICATION Items

No `[NEEDS CLARIFICATION]` markers exist in the spec. All decisions resolved above.

## Dependencies Verified

- `backend/auth.py` exports `get_current_user` — confirmed (line 31)
- `backend/db.py` exports `engine`, `get_session` — confirmed (lines 11, 18)
- `backend/models.py` exports `Task` with `user_id`, `completed`, `created_at` fields — confirmed
- `frontend/lib/auth-client.ts` exports `authClient` — confirmed
- `NEXT_PUBLIC_API_URL` env var used in frontend — confirmed in frontend CLAUDE.md
