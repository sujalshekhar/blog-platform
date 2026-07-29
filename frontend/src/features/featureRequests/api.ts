import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { toast } from "sonner";

export type FeatureStatus = "PENDING" | "ACCEPTED" | "DECLINED" | "COMPLETED";

export interface FeatureRequest {
  id: number;
  title: str;
  description: string;
  status: FeatureStatus;
  priority: number;
  category: string | null;
  requested_by: number;
  created_at: string;
  updated_at: string;
}

export interface FeatureRequestCreate {
  title: string;
  description: string;
  priority?: number;
  category?: string;
}

export const featureRequestsApi = {
  getFeatureRequests: async (): Promise<FeatureRequest[]> => {
    const response = await apiClient.get("/feature-requests/");
    return response.data;
  },
  createFeatureRequest: async (data: FeatureRequestCreate): Promise<FeatureRequest> => {
    const response = await apiClient.post("/feature-requests/", data);
    return response.data;
  },
  acceptFeatureRequest: async (id: number): Promise<FeatureRequest> => {
    const response = await apiClient.post(`/feature-requests/${id}/accept`);
    return response.data;
  },
  declineFeatureRequest: async (id: number): Promise<FeatureRequest> => {
    const response = await apiClient.post(`/feature-requests/${id}/decline`);
    return response.data;
  },
  completeFeatureRequest: async (id: number): Promise<FeatureRequest> => {
    const response = await apiClient.post(`/feature-requests/${id}/complete`);
    return response.data;
  },
};

export const useFeatureRequests = () => {
  return useQuery({
    queryKey: ["feature-requests"],
    queryFn: featureRequestsApi.getFeatureRequests,
  });
};

export const useCreateFeatureRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.createFeatureRequest,
    onSuccess: () => {
      toast.success("Feature request submitted successfully!");
      queryClient.invalidateQueries({ queryKey: ["feature-requests"] });
    },
    onError: () => {
      toast.error("Failed to submit feature request.");
    }
  });
};

export const useAcceptFeatureRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.acceptFeatureRequest,
    onSuccess: () => {
      toast.success("Feature request accepted!");
      queryClient.invalidateQueries({ queryKey: ["feature-requests"] });
    },
  });
};

export const useDeclineFeatureRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.declineFeatureRequest,
    onSuccess: () => {
      toast.success("Feature request declined.");
      queryClient.invalidateQueries({ queryKey: ["feature-requests"] });
    },
  });
};

export const useCompleteFeatureRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.completeFeatureRequest,
    onSuccess: () => {
      toast.success("Feature request marked as completed!");
      queryClient.invalidateQueries({ queryKey: ["feature-requests"] });
    },
  });
};
