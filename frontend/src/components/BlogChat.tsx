import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@/providers/AuthProvider";
import { useChatHistory, Message } from "@/features/chat/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send } from "lucide-react";

interface BlogChatProps {
  blogGroupId: number;
}

export function BlogChat({ blogGroupId }: BlogChatProps) {
  const { user, isAuthenticated } = useAuth();
  const { 
    data, 
    fetchNextPage, 
    hasNextPage, 
    isFetchingNextPage, 
    isLoading 
  } = useChatHistory(blogGroupId);
  const { sendMessage, isConnected } = useWebSocket(isAuthenticated);
  
  const [newMessages, setNewMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

  const historyMessages = data ? [...data.pages].reverse().flatMap(page => page) : [];
  
  const allMessages = React.useMemo(() => {
    const combined = [];
    const seen = new Set();
    for (const msg of [...historyMessages, ...newMessages]) {
      if (!seen.has(msg.id)) {
        seen.add(msg.id);
        combined.push(msg);
      }
    }
    return combined;
  }, [historyMessages, newMessages]);

  useEffect(() => {
    if (!isAuthenticated || !isConnected) return;

    sendMessage({ type: "subscribe", blog_group_id: blogGroupId });

    const handleNewMessage = (e: CustomEvent) => {
      const msgData = e.detail;
      console.log("Received WebSocket event:", msgData);
      if (msgData.type === "new_message") {
        console.log("Adding new message to state:", msgData.message);
        setShouldAutoScroll(true); // force scroll on new message
        setNewMessages((prev) => [...prev, msgData.message]);
      }
    };

    window.addEventListener("ws_message", handleNewMessage as EventListener);

    return () => {
      window.removeEventListener("ws_message", handleNewMessage as EventListener);
      sendMessage({ type: "unsubscribe", blog_group_id: blogGroupId });
    };
  }, [blogGroupId, isAuthenticated, isConnected, sendMessage]);

  // Auto-scroll logic
  useEffect(() => {
    if (shouldAutoScroll && scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
      setShouldAutoScroll(false);
    }
  }, [allMessages, shouldAutoScroll]);

  // Handle manual scroll to detect if we're near bottom to re-enable auto-scroll
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    const isNearBottom = target.scrollHeight - target.scrollTop - target.clientHeight < 50;
    if (isNearBottom) {
      setShouldAutoScroll(true);
    } else {
      setShouldAutoScroll(false);
    }
  };

  const handleLoadPrevious = async () => {
    const container = scrollContainerRef.current;
    const previousHeight = container?.scrollHeight || 0;
    
    await fetchNextPage();
    
    // Restore scroll position so it doesn't jump
    setTimeout(() => {
      if (container) {
        container.scrollTop = container.scrollHeight - previousHeight;
      }
    }, 50);
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    sendMessage({
      type: "message",
      blog_group_id: blogGroupId,
      content: inputText.trim()
    });
    
    setInputText("");
    setShouldAutoScroll(true);
  };

  if (!isAuthenticated) {
    return (
      <Card className="mt-8 border-dashed bg-muted/20">
        <CardContent className="p-8 text-center text-muted-foreground">
          Please log in to join the discussion.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-8 shadow-sm">
      <CardHeader className="bg-secondary/20 pb-4 border-b">
        <CardTitle className="text-lg">Discussion</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea 
          className="h-[400px] p-4" 
          viewportRef={scrollContainerRef}
          onScrollCapture={handleScroll}
        >
          {isLoading ? (
            <div className="text-center text-muted-foreground">Loading chat...</div>
          ) : allMessages.length === 0 ? (
            <div className="text-center text-muted-foreground pt-10">
              No comments yet. Be the first to start the discussion!
            </div>
          ) : (
            <div className="space-y-4">
              {hasNextPage && (
                <div className="flex justify-center pb-4">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleLoadPrevious}
                    disabled={isFetchingNextPage}
                  >
                    {isFetchingNextPage ? 'Loading...' : 'Load previous messages'}
                  </Button>
                </div>
              )}
              {allMessages.map((msg, index) => {
                const isMe = msg.author_id === user?.id;
                return (
                  <div key={msg.id || index} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-baseline space-x-2 mb-1">
                      <span className="text-xs font-semibold text-muted-foreground">
                        {isMe ? 'You' : `${msg.author.first_name} ${msg.author.last_name}`}
                      </span>
                      <span className="text-[10px] text-muted-foreground/50">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${
                      isMe 
                        ? 'bg-primary text-primary-foreground rounded-br-sm' 
                        : 'bg-muted rounded-bl-sm'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                );
              })}
              <div ref={scrollRef} />
            </div>
          )}
        </ScrollArea>
      </CardContent>
      <CardFooter className="p-3 border-t bg-secondary/10">
        <form onSubmit={handleSend} className="flex w-full space-x-2">
          <Input 
            value={inputText} 
            onChange={(e) => setInputText(e.target.value)} 
            placeholder="Type your comment..." 
            className="flex-1 rounded-full bg-background"
          />
          <Button type="submit" size="icon" className="rounded-full shrink-0" disabled={!inputText.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
