export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  user: AuthUser;
}

const AUTH_USER_KEY = "novasphere-auth-user";

export function getStoredUser() {
  if (typeof window === "undefined") {
    return null;
  }

  const rawValue = window.localStorage.getItem(AUTH_USER_KEY);
  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as AuthUser;
  } catch {
    return null;
  }
}

export function storeAuthSession(payload: AuthResponse) {
  window.localStorage.setItem(AUTH_USER_KEY, JSON.stringify(payload.user));
}

export function clearAuthSession() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(AUTH_USER_KEY);
}
