// Auth utilities
export interface AuthState {
  token: string | null;
  username: string | null;
  role: 'admin' | 'analyst' | 'viewer' | null;
  isAuthenticated: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  expires_in: number;
}

const TOKEN_KEY = 'aegis_token';
const USER_KEY = 'aegis_user';
const ROLE_KEY = 'aegis_role';

export const authUtils = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string, username: string, role: string): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
    localStorage.setItem(ROLE_KEY, role);
  },

  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ROLE_KEY);
  },

  getUsername(): string | null {
    return localStorage.getItem(USER_KEY);
  },

  getRole(): 'admin' | 'analyst' | 'viewer' | null {
    return (localStorage.getItem(ROLE_KEY) as any) || null;
  },

  getAuthState(): AuthState {
    const token = this.getToken();
    const username = this.getUsername();
    const role = this.getRole();
    return {
      token,
      username,
      role,
      isAuthenticated: !!token && !!username,
    };
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  hasRole(requiredRole: string): boolean {
    const role = this.getRole();
    if (!role) return false;

    const roleHierarchy: Record<string, number> = {
      admin: 3,
      analyst: 2,
      viewer: 1,
    };

    return (roleHierarchy[role] || 0) >= (roleHierarchy[requiredRole] || 0);
  },
};
