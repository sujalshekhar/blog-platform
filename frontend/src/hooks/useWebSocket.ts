import { useEffect, useRef, useState, useCallback } from "react";
import { getToken } from "@/api/client";

export function useWebSocket(isAuthenticated: boolean) {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (!isAuthenticated) {
      if (ws.current) {
        ws.current.close(1000, "User disconnected");
        ws.current = null;
      }
      return;
    }

    const connect = () => {
      const token = getToken();
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || "";
      let wsUrl = "";
      if (apiUrl) {
        const wsProtocol = apiUrl.startsWith("https") ? "wss:" : "ws:";
        const urlWithoutProtocol = apiUrl.replace(/^https?:\/\//, "");
        wsUrl = `${wsProtocol}//${urlWithoutProtocol}/ws?token=${token}`;
      } else {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        wsUrl = `${wsProtocol}//${window.location.host}/api/v1/ws?token=${token}`;
      }
      
      try {
        const socket = new WebSocket(wsUrl);
        ws.current = socket;

        socket.onopen = () => {
          if (ws.current === socket) {
            setIsConnected(true);
            reconnectAttempts.current = 0; // Reset attempts on success
          }
        };

        socket.onclose = (event) => {
          if (ws.current === socket) {
            setIsConnected(false);
            ws.current = null;
            
            // Reconnect logic
            if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
              const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
              reconnectTimeout.current = setTimeout(() => {
                reconnectAttempts.current += 1;
                connect();
              }, timeout);
            }
          }
        };

        socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          if (ws.current === socket) {
            socket.close();
          }
        };

        socket.onmessage = (event) => {
          // Parse JSON and dispatch event globally
          try {
            const parsed = JSON.parse(event.data);
            window.dispatchEvent(new CustomEvent("ws_message", { detail: parsed }));
          } catch (e) {
            // Might be plain text like 'pong'
            if (event.data === "pong") {
            }
          }
        };
      } catch (err) {
        console.error("Error creating WebSocket:", err);
      }
    };

    connect();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (ws.current) {
        // 1000 is normal closure
        ws.current.close(1000, "Component unmounted");
      }
    };
  }, [isAuthenticated]);

  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(typeof message === "string" ? message : JSON.stringify(message));
    } else {
      console.warn("WebSocket is not connected. Cannot send message.");
    }
  }, []);

  return { isConnected, sendMessage };
}
