"""
backend/groq_agent.py — Phase 3 Groq AI Agent
Defines GROQ_TOOLS schemas, execute_tool() dispatcher, and async run_agent().

Rules (Constitution Laws XII, XIV, XVII):
- Groq free tier only (llama-3.3-70b-versatile).
- max_tokens=1000 on every call.
- user_id NEVER in tool schemas — always injected by execute_tool().
- RateLimitError → retry once (1 s delay) then friendly message.
- All other exceptions → friendly error; never crash.
"""

import asyncio
import os

from dotenv import load_dotenv
from groq import AsyncGroq, BadRequestError, RateLimitError

import mcp_server

load_dotenv()

_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    """Lazily create the Groq client so imports work even without GROQ_API_KEY set yet."""
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def _build_system_prompt(user_name: str | None, user_email: str | None) -> str:
    profile = ""
    if user_name or user_email:
        parts = []
        if user_name:
            parts.append(f"full name: {user_name}")
        if user_email:
            parts.append(f"email: {user_email}")
        profile = f" The current user's {', '.join(parts)}."
    return (
        "You are a helpful AI assistant for a personal productivity app."
        f"{profile}"
        " You help users manage their tasks, view login activity, and get project statistics."
        " When asked for the user's name or email, use the profile information stated above — do not call a tool for it."
        " Always use the available tools to fetch real data — never make up information."
        " Be friendly, concise, and confirm every action clearly."
        " When a task action is performed, mention the task ID in your response."
    )

# ---------------------------------------------------------------------------
# Tool schemas (no user_id — always injected server-side)
# ---------------------------------------------------------------------------

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required, 1-200 chars)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks with optional status filter",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status. Default: all",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a specific task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to complete",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a specific task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional)",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails",
            "description": "Get recent emails from the user's inbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of emails to return (1-20, default 10)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_login_activity",
            "description": "Get recent login history for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of login events to return (default 10)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_stats",
            "description": (
                "Get a full overview of the user's project: "
                "task counts, conversations, last login"
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

def execute_tool(tool_name: str, arguments: dict, user_id: str) -> dict | list:
    """Dispatch to the correct MCP tool, injecting user_id."""
    dispatch = {
        "add_task": lambda: mcp_server.add_task(user_id, **arguments),
        "list_tasks": lambda: mcp_server.list_tasks(user_id, **arguments),
        "complete_task": lambda: mcp_server.complete_task(user_id, **arguments),
        "delete_task": lambda: mcp_server.delete_task(user_id, **arguments),
        "update_task": lambda: mcp_server.update_task(user_id, **arguments),
        "get_emails": lambda: mcp_server.get_emails(user_id, **arguments),
        "get_login_activity": lambda: mcp_server.get_login_activity(user_id, **arguments),
        "get_current_datetime": lambda: mcp_server.get_current_datetime(),
        "get_project_stats": lambda: mcp_server.get_project_stats(user_id),
    }
    fn = dispatch.get(tool_name)
    if fn is None:
        return {"error": f"Unknown tool: {tool_name}"}
    return fn()


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

def _looks_like_function_call(text: str) -> bool:
    """Detect when model outputs raw function-call XML instead of using tool_calls."""
    import re
    return bool(re.search(r'<function[=:$]\w+>', text or ""))


async def run_agent(
    user_id: str,
    messages: list,
    user_name: str | None = None,
    user_email: str | None = None,
) -> dict:
    """
    Run the Groq AI agent with tool-calling loop.
    Returns {"response": str, "tool_calls": list}.
    """
    full_messages = [{"role": "system", "content": _build_system_prompt(user_name, user_email)}] + messages
    tool_calls_made: list = []

    _rate_limited = False

    async def _call_groq(msgs: list, attempt: int = 1, use_tools: bool = True):
        nonlocal _rate_limited
        try:
            kwargs: dict = dict(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                max_tokens=1000,
            )
            if use_tools:
                kwargs["tools"] = GROQ_TOOLS
                kwargs["tool_choice"] = "auto"
            return await _get_client().chat.completions.create(**kwargs)
        except RateLimitError:
            if attempt == 1:
                await asyncio.sleep(1)
                return await _call_groq(msgs, attempt=2, use_tools=use_tools)
            _rate_limited = True
            return None  # rate limit exhausted after retry
        except BadRequestError:
            # Model generated malformed tool call syntax
            if attempt == 1 and use_tools:
                # First retry: same request with tools (often succeeds on retry)
                await asyncio.sleep(0.5)
                return await _call_groq(msgs, attempt=2, use_tools=True)
            if attempt == 2 and use_tools:
                # Second retry: fall back to no tools for a helpful text response
                return await _call_groq(msgs, attempt=3, use_tools=False)
            return None

    try:
        response = await _call_groq(full_messages)

        if response is None:
            if _rate_limited:
                msg = "I'm a bit busy right now due to high demand. Please try again in a moment!"
            else:
                msg = "Could not reach the AI service. Please try again."
            return {"response": msg, "tool_calls": []}

        choice = response.choices[0]

        # Tool-calling loop
        while choice.finish_reason == "tool_calls":
            tool_call_objs = choice.message.tool_calls or []
            # Serialize to plain dict — Groq SDK Pydantic objects cause TypeError on re-submission
            full_messages.append({
                "role": "assistant",
                "content": choice.message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_call_objs
                ],
            })

            for tc in tool_call_objs:
                import json as _json
                args = _json.loads(tc.function.arguments or "{}")
                result = execute_tool(tc.function.name, args, user_id)
                tool_calls_made.append({"tool": tc.function.name, "result": result})

                full_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": _json.dumps(result),
                    }
                )

            # Get final response after tool results
            follow_up = await _call_groq(full_messages)
            if follow_up is None:
                return {
                    "response": "I encountered an issue processing the tool results. Please try again.",
                    "tool_calls": tool_calls_made,
                }
            choice = follow_up.choices[0]

        final_text = choice.message.content or "I'm not sure how to respond to that."

        # Rescue: model sometimes outputs malformed function call as text
        # e.g. <function=update_task>{"task_id": 1, "title": "foo"}</function>
        # Parse and execute it ourselves so the action isn't lost.
        if not tool_calls_made and _looks_like_function_call(final_text):
            import json as _json, re as _re
            m = _re.search(r'<function[=:$](\w+)>\s*(\{.*?\})', final_text, _re.DOTALL)
            if m:
                rescued_tool = m.group(1)
                try:
                    rescued_args = _json.loads(m.group(2))
                    rescued_result = execute_tool(rescued_tool, rescued_args, user_id)
                    tool_calls_made.append({"tool": rescued_tool, "result": rescued_result})
                    # Ask model to summarise the result in plain English
                    summary_msgs = full_messages + [
                        {"role": "user", "content": "Result: %s. Confirm in one friendly sentence." % _json.dumps(rescued_result)},
                    ]
                    summary = await _call_groq(summary_msgs, use_tools=False)
                    if summary:
                        final_text = summary.choices[0].message.content or final_text
                except Exception:
                    pass  # keep original text if rescue fails

        return {"response": final_text, "tool_calls": tool_calls_made}

    except Exception as exc:
        return {
            "response": f"Sorry, I encountered an unexpected error. Please try again! ({type(exc).__name__})",
            "tool_calls": [],
        }
