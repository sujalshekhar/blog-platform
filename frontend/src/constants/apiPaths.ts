export const API_PATHS = {
  BLOGS: {
    BASE: "/blogs",
    APPROVED: "/blogs/",
    MY_BLOGS: "/blogs/my-blogs",
    MY_DRAFTS: "/blogs/my-drafts",
    ALL_ACTIVE: "/blogs/all",
    BY_ID: (id: number) => `/blogs/${id}`,
    SUBMIT: (id: number) => `/blogs/${id}/submit`,
    APPROVE: (id: number) => `/blogs/${id}/approve`,
    REJECT: (id: number) => `/blogs/${id}/reject`,
    HISTORY: (id: number) => `/blogs/${id}/history`,
  },
  CHAT: {
    HISTORY: (blogGroupId: number) => `/chat/${blogGroupId}`,
  },
  FEATURE_REQUESTS: {
    BASE: "/feature-requests/",
    UPDATE_STATUS: (id: number) => `/feature-requests/${id}`,
  },
  NOTIFICATIONS: {
    BASE: "/notifications/",
    MARK_READ: (id: number) => `/notifications/${id}/read`,
  },
  USER: {
    ME: "/users/me",
  }
} as const;
