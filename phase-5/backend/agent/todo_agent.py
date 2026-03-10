"""Todo Agent using OpenAI Agents SDK.

This module implements the AI agent that processes natural language
commands and uses MCP tools to manage tasks.
"""

import json
import os
import time
from typing import Any

from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from dotenv import load_dotenv

from mcp.server import create_tool_router, MCPToolRouter

# Load environment variables
load_dotenv()

# Retry configuration
MAX_RETRIES = 2  # Reduced retries for faster failure
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 5.0  # seconds - faster failure


class TodoAgent:
    """AI Agent for managing todo tasks through natural language."""

    SYSTEM_PROMPT = """You are a helpful and friendly todo list assistant. Your job is to help users manage their tasks through natural language conversation.

You have access to the following tools:
- add_task: Create new tasks
- list_tasks: Show all tasks
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Modify task title or description

## Confirmation Guidelines (IMPORTANT):
Always confirm actions with a friendly, personalized response:
- After adding: "Great! I've added '[task name]' to your list. You now have X tasks."
- After completing: "Awesome! '[task name]' is now marked as done. Keep up the great work!"
- After deleting: "Done! I've removed '[task name]' from your list."
- After updating: "Got it! I've updated '[task name]' with the new details."
- After listing: Provide a nicely formatted list with status indicators (✓ for done, ○ for pending).

## Error Handling Guidelines (IMPORTANT):
Handle errors gracefully with helpful suggestions:
- Task not found: "I couldn't find a task with ID X. Would you like me to show your current tasks so you can find the right one?"
- No tasks: "Your task list is empty! Would you like to add your first task?"
- Invalid input: "I didn't quite understand that. Could you try rephrasing? For example, 'Add a task to buy groceries' or 'Show my tasks'."
- Operation failed: Explain what went wrong in simple terms and suggest what the user can do next.

## Task ID Inquiry (IMPORTANT):
When a user says "I want to complete/delete/update a task" without specifying which one:
1. First show their current tasks with IDs using list_tasks
2. Then ask: "Which task would you like to [complete/delete/update]? Please tell me the task ID or number."
3. Wait for the user to provide the ID before performing the action

## General Guidelines:
1. Be warm, encouraging, and conversational in your responses.
2. When listing tasks, format them nicely with task IDs, status indicators, and titles.
3. If a user's request is unclear, ask for clarification politely.
4. For task operations requiring an ID, if the user refers to a task by name, first list tasks to find the ID, then perform the operation.
5. If the user sends gibberish or nonsensical input, politely ask them to rephrase.
6. If the user asks about unrelated topics, kindly remind them you're a todo assistant.
7. When multiple tasks match a name reference, list them and ask which one they mean.
8. Use emojis sparingly to keep responses friendly but professional.
9. Be efficient - don't ask unnecessary questions if the user provides all needed information.

Remember: You can only manage the user's own tasks. Each user has their own separate task list."""

    def __init__(self, user_id: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the Todo Agent.

        Args:
            user_id: The ID of the authenticated user
            model: The model to use
        """
        self.user_id = user_id
        self.model = model
        self.tool_router: MCPToolRouter = create_tool_router(user_id)
        self.client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0,
        )

    def _call_with_retry(self, messages: list, tools: list) -> Any:
        """
        Call OpenAI API with exponential backoff retry logic.

        Args:
            messages: The messages to send
            tools: The tools available to the agent

        Returns:
            The API response

        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        delay = INITIAL_RETRY_DELAY

        for attempt in range(MAX_RETRIES):
            try:
                print(f"[DEBUG] Attempt {attempt + 1}: Calling Grok API...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )
                print(f"[DEBUG] Grok API responded successfully")
                return response
            except RateLimitError as e:
                print(f"[DEBUG] RateLimitError: {e}")
                last_exception = e
                # Rate limited - wait and retry
                retry_after = getattr(e, 'retry_after', None)
                if retry_after:
                    wait_time = float(retry_after)
                else:
                    wait_time = min(delay * (2 ** attempt), MAX_RETRY_DELAY)
                time.sleep(wait_time)
            except APIConnectionError as e:
                print(f"[DEBUG] APIConnectionError: {e}")
                last_exception = e
                # Connection error - retry with backoff
                wait_time = min(delay * (2 ** attempt), MAX_RETRY_DELAY)
                time.sleep(wait_time)
            except APIError as e:
                print(f"[DEBUG] APIError: {e}")
                # Server error (5xx) - retry; client error (4xx) - don't retry
                if e.status_code and 500 <= e.status_code < 600:
                    last_exception = e
                    wait_time = min(delay * (2 ** attempt), MAX_RETRY_DELAY)
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"[DEBUG] Unexpected error: {type(e).__name__}: {e}")
                raise

        # All retries exhausted
        print(f"[DEBUG] All retries exhausted. Last error: {last_exception}")
        raise last_exception or Exception("All retries exhausted")

    def _process_tool_calls(self, tool_calls: list) -> list[dict[str, Any]]:
        """
        Process tool calls from the model response.

        Args:
            tool_calls: List of tool calls from OpenAI response

        Returns:
            List of tool results
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            result = self.tool_router.execute_tool(tool_name, arguments)

            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result),
            })

        return results

    def chat(
        self, user_message: str, conversation_history: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """
        Process a user message and return the agent's response.

        Args:
            user_message: The user's natural language message
            conversation_history: Optional list of previous messages

        Returns:
            Dict containing response text and any tool calls made
        """
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        # Get available tools
        tools = self.tool_router.get_available_tools()

        # Track tool calls for this interaction
        all_tool_calls = []

        # Agentic loop - continue until no more tool calls
        while True:
            response = self._call_with_retry(messages, tools)
            assistant_message = response.choices[0].message

            # If no tool calls, we're done
            if not assistant_message.tool_calls:
                return {
                    "response": assistant_message.content or "",
                    "tool_calls": all_tool_calls,
                    "messages": messages[1:],  # Exclude system prompt
                }

            # Process tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ],
            })

            # Execute tools and add results
            tool_results = self._process_tool_calls(assistant_message.tool_calls)
            messages.extend(tool_results)

            # Track tool calls
            for tc in assistant_message.tool_calls:
                all_tool_calls.append({
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })


def create_agent(user_id: str, model: str | None = None) -> TodoAgent:
    """
    Factory function to create a TodoAgent.

    Args:
        user_id: The ID of the authenticated user
        model: Optional model override

    Returns:
        Configured TodoAgent instance
    """
    if model:
        return TodoAgent(user_id, model=model)
    return TodoAgent(user_id)
