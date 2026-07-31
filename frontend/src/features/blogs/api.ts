import { apiClient } from "@/api/client";
import { Blog } from "@/types";
import { useQuery } from "@tanstack/react-query";
import { API_PATHS } from "@/constants/apiPaths";
import { QUERY_KEYS } from "@/constants/queryKeys";

export const blogsApi = {
  /** Fetch approved blogs (public feed) */
  getApprovedBlogs: async (skip: number = 0, limit: number = 9, search?: string, blog_type?: string, sort_by?: string, sort_order?: string) => {
    let url = `${API_PATHS.BLOGS.APPROVED}?skip=${skip}&limit=${limit}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (blog_type && blog_type !== "ALL") url += `&blog_type=${blog_type}`;
    if (sort_by) url += `&sort_by=${sort_by}`;
    if (sort_order) url += `&sort_order=${sort_order}`;
    const response = await apiClient.get<Blog[]>(url);
    return response.data;
  },
  /** Fetch blogs authored by the current user */
  getMyBlogs: async (skip: number = 0, limit: number = 9) => {
    const response = await apiClient.get<Blog[]>(`${API_PATHS.BLOGS.MY_BLOGS}?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  /** Fetch drafts authored by the current user */
  getMyDrafts: async (skip: number = 0, limit: number = 9) => {
    const response = await apiClient.get<Blog[]>(`${API_PATHS.BLOGS.MY_DRAFTS}?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  /** Fetch all active blogs regardless of status (Admin) */
  getAllActiveBlogs: async (skip: number = 0, limit: number = 9) => {
    const response = await apiClient.get<Blog[]>(`${API_PATHS.BLOGS.ALL_ACTIVE}?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  /** Fetch a specific blog by ID */
  getBlogById: async (blog_id: number) => {
    const response = await apiClient.get<Blog>(API_PATHS.BLOGS.BY_ID(blog_id));
    return response.data;
  },
  /** Create a new draft blog */
  createBlog: async (data: { title: string; content: string; cover_image_url?: string; blog_type: string }) => {
    const response = await apiClient.post<Blog>(API_PATHS.BLOGS.BASE + "/", data);
    return response.data;
  },
  /** Update an existing blog (creates a new version) */
  updateBlog: async (blog_id: number, data: { title: string; content: string; cover_image_url?: string; blog_type: string }) => {
    const response = await apiClient.put<Blog>(API_PATHS.BLOGS.BY_ID(blog_id), data);
    return response.data;
  },
  /** Soft delete a blog */
  deleteBlog: async (blog_id: number) => {
    await apiClient.delete(API_PATHS.BLOGS.BY_ID(blog_id));
  },
  /** Submit a draft blog for review */
  submitBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(API_PATHS.BLOGS.SUBMIT(blog_id));
    return response.data;
  },
  /** Approve a pending blog */
  approveBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(API_PATHS.BLOGS.APPROVE(blog_id));
    return response.data;
  },
  /** Reject a pending blog */
  rejectBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(API_PATHS.BLOGS.REJECT(blog_id));
    return response.data;
  },
  /** Fetch all historical versions of a blog */
  getBlogHistory: async (blog_id: number) => {
    const response = await apiClient.get<Blog[]>(API_PATHS.BLOGS.HISTORY(blog_id));
    return response.data;
  }
};

// React Query Hooks

/** Query hook to fetch approved blogs for the home feed */
export const useApprovedBlogs = (skip: number = 0, limit: number = 9, search?: string, blog_type?: string, sort_by?: string, sort_order?: string) => 
  useQuery({ queryKey: [...QUERY_KEYS.BLOGS.APPROVED, skip, limit, search, blog_type, sort_by, sort_order], queryFn: () => blogsApi.getApprovedBlogs(skip, limit, search, blog_type, sort_by, sort_order) });

/** Query hook to fetch blogs authored by the current user */
export const useMyBlogs = (skip: number = 0, limit: number = 9) => 
  useQuery({ queryKey: [...QUERY_KEYS.BLOGS.MY_BLOGS, skip, limit], queryFn: () => blogsApi.getMyBlogs(skip, limit) });

/** Query hook to fetch draft blogs authored by the current user */
export const useMyDrafts = (skip: number = 0, limit: number = 9) => 
  useQuery({ queryKey: [...QUERY_KEYS.BLOGS.MY_DRAFTS, skip, limit], queryFn: () => blogsApi.getMyDrafts(skip, limit) });

/** Query hook to fetch all active blogs (Admin) */
export const useAllActiveBlogs = (skip: number = 0, limit: number = 9) => 
  useQuery({ queryKey: [...QUERY_KEYS.BLOGS.ALL_ACTIVE, skip, limit], queryFn: () => blogsApi.getAllActiveBlogs(skip, limit) });

/** Query hook to fetch a single blog */
export const useBlog = (id: number) => 
  useQuery({ queryKey: QUERY_KEYS.BLOGS.DETAIL(id), queryFn: () => blogsApi.getBlogById(id), enabled: !!id });

/** Query hook to fetch history of a blog */
export const useBlogHistory = (id: number) => 
  useQuery({ queryKey: QUERY_KEYS.BLOGS.HISTORY(id), queryFn: () => blogsApi.getBlogHistory(id), enabled: !!id });
