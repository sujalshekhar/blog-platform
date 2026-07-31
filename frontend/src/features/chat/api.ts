import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { API_PATHS } from "@/constants/apiPaths";
import { QUERY_KEYS } from "@/constants/queryKeys";

export interface UserInfo {
  id: number;
  first_name: string;
  last_name: string;
}

export interface Message {
  id: number;
  chat_id: number;
  author_id: number;
  content: string;
  created_at: string;
  author: UserInfo;
}

export const chatApi = {
  /** Fetch paginated chat history for a blog */
  getChatHistory: async (blogGroupId: number, cursor?: number, limit = 50): Promise<Message[]> => {
    let url = `${API_PATHS.CHAT.HISTORY(blogGroupId)}?limit=${limit}`;
    if (cursor) {
      url += `&cursor=${cursor}`;
    }
    const response = await apiClient.get(url);
    return response.data;
  },
};

/** Infinite query hook to fetch chat messages */
export const useChatHistory = (blogGroupId: number) => {
  return useInfiniteQuery({
    queryKey: QUERY_KEYS.CHAT.HISTORY(blogGroupId),
    queryFn: ({ pageParam }) => chatApi.getChatHistory(blogGroupId, pageParam),
    initialPageParam: undefined as number | undefined,
    getNextPageParam: (lastPage) => {
      // The backend returns them chronologically (oldest first). 
      // The first item is the oldest message we fetched in this batch.
      // If we got fewer than 50 messages, there are no older messages.
      if (lastPage.length < 50) return undefined;
      return lastPage[0]?.id;
    },
    enabled: !!blogGroupId,
  });
};
