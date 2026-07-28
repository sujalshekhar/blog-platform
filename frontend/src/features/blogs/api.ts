import { apiClient } from "@/api/client";
import { Blog } from "@/types";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export const blogsApi = {
  getApprovedBlogs: async () => {
    const response = await apiClient.get<Blog[]>("/blogs/");
    return response.data;
  },
  getMyBlogs: async () => {
    const response = await apiClient.get<Blog[]>("/blogs/my-blogs");
    return response.data;
  },
  getMyDrafts: async () => {
    const response = await apiClient.get<Blog[]>("/blogs/my-drafts");
    return response.data;
  },
  getAllActiveBlogs: async () => {
    const response = await apiClient.get<Blog[]>("/blogs/all");
    return response.data;
  },
  getBlogById: async (blog_id: number) => {
    const response = await apiClient.get<Blog>(`/blogs/${blog_id}`);
    return response.data;
  },
  createBlog: async (data: { title: string; content: string; cover_image_url?: string }) => {
    const response = await apiClient.post<Blog>("/blogs/", data);
    return response.data;
  },
  updateBlog: async (blog_id: number, data: { title: string; content: string; cover_image_url?: string }) => {
    const response = await apiClient.put<Blog>(`/blogs/${blog_id}`, data);
    return response.data;
  },
  deleteBlog: async (blog_id: number) => {
    await apiClient.delete(`/blogs/${blog_id}`);
  },
  submitBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(`/blogs/${blog_id}/submit`);
    return response.data;
  },
  approveBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(`/blogs/${blog_id}/approve`);
    return response.data;
  },
  rejectBlog: async (blog_id: number) => {
    const response = await apiClient.post<Blog>(`/blogs/${blog_id}/reject`);
    return response.data;
  },
  getBlogHistory: async (blog_id: number) => {
    const response = await apiClient.get<Blog[]>(`/blogs/${blog_id}/history`);
    return response.data;
  }
};

// React Query Hooks
export const useApprovedBlogs = () => useQuery({ queryKey: ["blogs", "approved"], queryFn: blogsApi.getApprovedBlogs });
export const useMyBlogs = () => useQuery({ queryKey: ["blogs", "my-blogs"], queryFn: blogsApi.getMyBlogs });
export const useMyDrafts = () => useQuery({ queryKey: ["blogs", "my-drafts"], queryFn: blogsApi.getMyDrafts });
export const useAllActiveBlogs = () => useQuery({ queryKey: ["blogs", "all-active"], queryFn: blogsApi.getAllActiveBlogs });
export const useBlog = (id: number) => useQuery({ queryKey: ["blogs", id], queryFn: () => blogsApi.getBlogById(id), enabled: !!id });
export const useBlogHistory = (id: number) => useQuery({ queryKey: ["blogs", "history", id], queryFn: () => blogsApi.getBlogHistory(id), enabled: !!id });
