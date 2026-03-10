"""MCP Server setup for Todo chatbot.

This module provides the MCP server configuration and tool routing
for the AI agent to interact with the task management system.
"""

from typing import Any

from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_all_tools,
)


class MCPToolRouter:
    """Routes tool calls to their corresponding implementations."""

    def __init__(self, user_id: str):
        """
        Initialize the tool router with a user context.

        Args:
            user_id: The ID of the authenticated user
        """
        self.user_id = user_id
        self._tools = {
            "add_task": self._add_task,
            "list_tasks": self._list_tasks,
            "complete_task": self._complete_task,
            "delete_task": self._delete_task,
            "update_task": self._update_task,
        }

    def _add_task(self, **kwargs) -> dict[str, Any]:
        """Route add_task with user context."""
        return add_task(self.user_id, **kwargs)

    def _list_tasks(self, **kwargs) -> dict[str, Any]:
        """Route list_tasks with user context."""
        return list_tasks(self.user_id, **kwargs)

    def _complete_task(self, **kwargs) -> dict[str, Any]:
        """Route complete_task with user context."""
        return complete_task(self.user_id, **kwargs)

    def _delete_task(self, **kwargs) -> dict[str, Any]:
        """Route delete_task with user context."""
        return delete_task(self.user_id, **kwargs)

    def _update_task(self, **kwargs) -> dict[str, Any]:
        """Route update_task with user context."""
        return update_task(self.user_id, **kwargs)

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: The name of the tool to execute
            arguments: The arguments to pass to the tool

        Returns:
            The result of the tool execution

        Raises:
            ValueError: If tool_name is not recognized
        """
        if tool_name not in self._tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        try:
            return self._tools[tool_name](**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }

    def get_available_tools(self) -> list[dict[str, Any]]:
        """Get the list of available tools for OpenAI function calling."""
        return get_all_tools()


def create_tool_router(user_id: str) -> MCPToolRouter:
    """
    Factory function to create a tool router for a user.

    Args:
        user_id: The ID of the authenticated user

    Returns:
        Configured MCPToolRouter instance
    """
    return MCPToolRouter(user_id)
