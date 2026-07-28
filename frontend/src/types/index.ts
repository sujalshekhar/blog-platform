export type UserRole = "USER" | "APPROVER" | "ADMIN";

export interface User {
  id: number;
  first_name: string;
  last_name?: string | null;
  email: string;
  role: UserRole;
}

export type BlogStatus = "DRAFT" | "PENDING" | "APPROVED" | "REJECTED";

export interface Blog {
  id: number;
  blog_group_id: number;
  version: number;
  title: string;
  content: string;
  cover_image_url?: string | null;
  status: BlogStatus;
  author_id: number;
  author?: {
    id: number;
    first_name: string;
    last_name?: string | null;
  };
  approved_by?: number | null;
  approved_at?: string | null;
  is_active_version: boolean;
  created_at: string;
  updated_at: string;
}
