import { create } from "zustand";
import { apiClient } from "./api-client";
import type { User, LoginRequest, RegisterRequest, TokenResponse } from "./types";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<any>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  login: async (credentials: LoginRequest) => {
    try {
      set({ isLoading: true, error: null });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
            mfa_code: credentials.mfa_code,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();

      // Check if MFA is required
      if (data.requires_mfa) {
        set({ isLoading: false });
        return data; // Return for the UI to handle MFA prompt
      }

      // Store tokens (they're nested in token object)
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", data.token.access_token);
        localStorage.setItem("refresh_token", data.token.refresh_token);
      }

      // Set user from response
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return data;
    } catch (error: any) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error.message || "Login failed",
      });
      throw error;
    }
  },

  register: async (data: RegisterRequest) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.post<User>("/api/v1/auth/register", data);

      // Auto-login after registration
      await useAuthStore.getState().login({
        email: data.email,
        password: data.password,
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.detail || "Registration failed",
      });
      throw error;
    }
  },

  logout: () => {
    // Clear tokens
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }

    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  },

  fetchUser: async () => {
    try {
      // Check if we have a token
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      if (!token) {
        set({ isLoading: false, isAuthenticated: false });
        return;
      }

      set({ isLoading: true });

      const user = await apiClient.get<User>("/api/v1/auth/me");

      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      // If fetch fails, clear tokens and mark as unauthenticated
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }

      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null, // Don't set error for failed auth check
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
