import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  content: string; // JSON string
  is_read: boolean;
  created_at: string;
}

export const notificationsApi = {
  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiClient.get("/notifications/");
    return response.data;
  },
  markAsRead: async (id: number): Promise<void> => {
    await apiClient.put(`/notifications/${id}/read`);
  },
};

export const useNotifications = () => {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: notificationsApi.getNotifications,
  });
};

export const useMarkAsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: notificationsApi.markAsRead,
    onMutate: async (notificationId) => {
      await queryClient.cancelQueries({ queryKey: ["notifications"] });
      
      const previousNotifications = queryClient.getQueryData<Notification[]>(["notifications"]);
      
      if (previousNotifications) {
        queryClient.setQueryData<Notification[]>(
          ["notifications"],
          previousNotifications.map((n) =>
            n.id === notificationId ? { ...n, is_read: true } : n
          )
        );
      }
      
      return { previousNotifications };
    },
    onError: (err, variables, context) => {
      if (context?.previousNotifications) {
        queryClient.setQueryData(["notifications"], context.previousNotifications);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};
