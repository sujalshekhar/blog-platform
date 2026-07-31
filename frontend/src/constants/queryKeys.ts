export const QUERY_KEYS = {
  BLOGS: {
    ALL: ["blogs"] as const,
    APPROVED: ["blogs", "approved"] as const,
    MY_BLOGS: ["blogs", "my-blogs"] as const,
    MY_DRAFTS: ["blogs", "my-drafts"] as const,
    ALL_ACTIVE: ["blogs", "all-active"] as const,
    DETAIL: (id: number) => ["blogs", id] as const,
    HISTORY: (id: number) => ["blogs", "history", id] as const,
  },
  CHAT: {
    HISTORY: (blogGroupId: number) => ["chat", blogGroupId] as const,
  },
  FEATURE_REQUESTS: {
    ALL: ["feature-requests"] as const,
  },
  NOTIFICATIONS: {
    ALL: ["notifications"] as const,
  },
  USER: {
    ME: ["user", "me"] as const,
  }
} as const;
