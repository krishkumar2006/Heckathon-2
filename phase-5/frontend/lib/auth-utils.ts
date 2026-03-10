/**
 * Authentication utility functions for the Todo Chatbot.
 */

/**
 * Get the current user from the stored token.
 * Returns null if no valid token exists.
 */
export function getCurrentUser(): { id: string; email: string } | null {
  if (typeof window === "undefined") {
    return null;
  }

  const token = localStorage.getItem("auth_token");
  if (!token) {
    return null;
  }

  try {
    // Token format: header.payload.signature
    const parts = token.split(".");
    if (parts.length !== 3) {
      return null;
    }

    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      // Token expired, clear it
      localStorage.removeItem("auth_token");
      return null;
    }

    return {
      id: payload.sub || payload.user_id || "unknown",
      email: payload.email || "user@example.com",
    };
  } catch {
    // Invalid token format
    return null;
  }
}

/**
 * Check if the current token is valid and not expired.
 */
export function isTokenValid(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const token = localStorage.getItem("auth_token");
  if (!token) {
    return false;
  }

  try {
    const parts = token.split(".");
    if (parts.length !== 3) {
      return false;
    }

    const payload = JSON.parse(atob(parts[1]));

    // Check expiration
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

/**
 * Logout the current user by clearing the auth token.
 * Optionally redirects to the signin page.
 */
export function logout(redirect: boolean = true): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem("auth_token");

  if (redirect) {
    window.location.href = "/";
  }
}

/**
 * Get the user's display name from the email.
 */
export function getUserDisplayName(): string {
  const user = getCurrentUser();
  if (!user) {
    return "User";
  }

  // Extract name from email (before @)
  const emailPart = user.email.split("@")[0];
  // Capitalize first letter
  return emailPart.charAt(0).toUpperCase() + emailPart.slice(1);
}
