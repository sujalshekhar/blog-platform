import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { toast } from "sonner";
import { API_PATHS } from "@/constants/apiPaths";
import { QUERY_KEYS } from "@/constants/queryKeys";

export type FeatureStatus = "PENDING" | "ACCEPTED" | "DECLINED" | "COMPLETED";

export interface FeatureRequest {
  id: number;
  title: string;
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
  /** Fetch all feature requests (admin sees all, users see their own) */
  getFeatureRequests: async (): Promise<FeatureRequest[]> => {
    const response = await apiClient.get(API_PATHS.FEATURE_REQUESTS.BASE);
    return response.data;
  },
  /** Create a new feature request */
  createFeatureRequest: async (data: FeatureRequestCreate): Promise<FeatureRequest> => {
    const response = await apiClient.post(API_PATHS.FEATURE_REQUESTS.BASE, data);
    return response.data;
  },
  /** Update the status of a feature request (Admin) */
  updateFeatureRequestStatus: async (params: { id: number; status: FeatureStatus }): Promise<FeatureRequest> => {
    const response = await apiClient.patch(API_PATHS.FEATURE_REQUESTS.UPDATE_STATUS(params.id), { status: params.status });
    return response.data;
  },
};

/** Hook to fetch feature requests */
export const useFeatureRequests = () => {
  return useQuery({
    queryKey: QUERY_KEYS.FEATURE_REQUESTS.ALL,
    queryFn: featureRequestsApi.getFeatureRequests,
  });
};

/** Hook to create a feature request */
export const useCreateFeatureRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.createFeatureRequest,
    onSuccess: () => {
      toast.success("Feature request submitted successfully!");
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.FEATURE_REQUESTS.ALL });
    },
    onError: () => {
      toast.error("Failed to submit feature request.");
    }
  });
};

/** Hook to update a feature request status */
export const useUpdateFeatureRequestStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: featureRequestsApi.updateFeatureRequestStatus,
    onSuccess: (data) => {
      toast.success(`Feature request marked as ${data.status.toLowerCase()}`);
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.FEATURE_REQUESTS.ALL });
    },
    onError: () => {
      toast.error("Failed to update feature request status.");
    }
  });
};
