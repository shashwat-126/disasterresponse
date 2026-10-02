
import axios from "axios";
import { API_BASE_URL } from "../utils/constants";

const client = axios.create({ baseURL: API_BASE_URL, timeout: 10000 });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("eadrp_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("eadrp_token");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default client;
