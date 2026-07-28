import { apiClient } from "@/api/client";
import { User } from "@/types";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  login: async (data: any): Promise<TokenResponse> => {
    // The FastAPI OAuth2PasswordRequestForm expects form data
    const formData = new URLSearchParams();
    formData.append("username", data.email);
    formData.append("password", data.password);
    
    const response = await apiClient.post<TokenResponse>("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    return response.data;
  },

  register: async (data: any): Promise<User> => {
    const response = await apiClient.post<User>("/auth/register", data);
    return response.data;
  }
};
