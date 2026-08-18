import axios from "axios";

const serviceApiUrl = process.env.NEXT_PUBLIC_BACKEND_URL
  ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/v1`
  : undefined;
const defaultApiUrl =
  process.env.NODE_ENV === "production" ? "/api/v1" : "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? serviceApiUrl ?? defaultApiUrl,
  headers: { "Content-Type": "application/json" },
  timeout: 10_000,
  withCredentials: true,
});
