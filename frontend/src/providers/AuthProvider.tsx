import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/types";
import { getToken, removeToken } from "@/api/client";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User, token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const isAuthenticated = !!getToken() && !!user;

  useEffect(() => {
    let eventSource: EventSource | null = null;

    if (isAuthenticated) {
      const token = getToken();
      if (token) {
        const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        eventSource = new EventSource(`${baseUrl}/api/v1/sse/stream?token=${token}`);

        eventSource.addEventListener("notification", (event) => {
          try {
            const data = JSON.parse(event.data);
            toast(data.title, {
              description: data.message,
            });
            // Immediately refetch notifications to update unread badge
            queryClient.invalidateQueries({ queryKey: ["notifications"] });
          } catch (e) {
            console.error("Failed to parse notification", e);
          }
        });

        eventSource.onerror = (error) => {
          console.error("SSE Error:", error);
          // Let browser attempt reconnect automatically
        };
      }
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [isAuthenticated]);

  const login = (userData: User, token: string) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("token", token);
  };

  const logout = () => {
    setUser(null);
    removeToken();
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
