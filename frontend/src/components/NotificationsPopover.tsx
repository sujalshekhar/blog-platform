import { useState, useMemo } from "react";
import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useNotifications, useMarkAsRead } from "@/features/notifications/api";
import { useNavigate } from "react-router-dom";

export function NotificationsPopover() {
  const [open, setOpen] = useState(false);
  const { data: notifications = [], isLoading } = useNotifications();
  const markAsRead = useMarkAsRead();
  const navigate = useNavigate();

  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !n.is_read).length;
  }, [notifications]);

  const handleNotificationClick = (notification: any) => {
    if (!notification.is_read) {
      markAsRead.mutate(notification.id);
    }
    
    // Parse the content if it's JSON
    try {
      const content = JSON.parse(notification.content);
      if (content.blog_id) {
        setOpen(false);
        navigate(`/blogs/${content.blog_id}`);
      }
    } catch (e) {
      console.error("Could not parse notification content", e);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative rounded-full hover:bg-secondary/50">
          <Bell className="h-5 w-5 text-muted-foreground" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-2 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <h4 className="font-semibold text-sm">Notifications</h4>
          {unreadCount > 0 && (
            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">
              {unreadCount} new
            </span>
          )}
        </div>
        
        <ScrollArea className="h-80">
          {isLoading ? (
            <div className="p-4 text-center text-sm text-muted-foreground">Loading...</div>
          ) : notifications.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">No notifications yet</div>
          ) : (
            <div className="flex flex-col">
              {notifications.map((notification) => {
                let parsedContent: any = { message: notification.content };
                try {
                  parsedContent = JSON.parse(notification.content);
                } catch (e) {}

                return (
                  <button
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`flex flex-col gap-1 p-4 text-left text-sm transition-colors hover:bg-muted/50 border-b last:border-0 ${
                      !notification.is_read ? "bg-primary/5 dark:bg-primary/10" : ""
                    }`}
                  >
                    <div className="flex w-full items-start justify-between gap-2">
                      <span className={`font-semibold ${!notification.is_read ? "text-foreground" : "text-muted-foreground"}`}>
                        {parsedContent.title || "Notification"}
                      </span>
                      {!notification.is_read && (
                        <span className="flex h-2 w-2 rounded-full bg-primary flex-shrink-0 mt-1.5" />
                      )}
                    </div>
                    <span className={`text-xs ${!notification.is_read ? "text-foreground/80" : "text-muted-foreground"}`}>
                      {parsedContent.message}
                    </span>
                    <span className="text-[10px] text-muted-foreground/60 mt-1">
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
