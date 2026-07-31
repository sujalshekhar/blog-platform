import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { API_PATHS } from "@/constants/apiPaths";
import { QUERY_KEYS } from "@/constants/queryKeys";

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  content: string; // JSON string
  is_read: boolean;
  created_at: string;
}

export const notificationsApi = {
  /** Fetch all notifications for the current user */
  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiClient.get(API_PATHS.NOTIFICATIONS.BASE);
    return response.data;
  },
  /** Mark a specific notification as read */
  markAsRead: async (id: number): Promise<void> => {
    await apiClient.put(API_PATHS.NOTIFICATIONS.MARK_READ(id));
  },
};

/** Hook to fetch notifications */
export const useNotifications = () => {
  return useQuery({
    queryKey: QUERY_KEYS.NOTIFICATIONS.ALL,
    queryFn: notificationsApi.getNotifications,
  });
};

/** Hook to mark a notification as read (with optimistic updates) */
export const useMarkAsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: notificationsApi.markAsRead,
    onMutate: async (notificationId) => {
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.NOTIFICATIONS.ALL });
      
      const previousNotifications = queryClient.getQueryData<Notification[]>(QUERY_KEYS.NOTIFICATIONS.ALL);
      
      if (previousNotifications) {
        queryClient.setQueryData<Notification[]>(
          QUERY_KEYS.NOTIFICATIONS.ALL,
          previousNotifications.map((n) =>
            n.id === notificationId ? { ...n, is_read: true } : n
          )
        );
      }
      
      return { previousNotifications };
    },
    onError: (err, variables, context) => {
      if (context?.previousNotifications) {
        queryClient.setQueryData(QUERY_KEYS.NOTIFICATIONS.ALL, context.previousNotifications);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.NOTIFICATIONS.ALL });
    },
  });
};
