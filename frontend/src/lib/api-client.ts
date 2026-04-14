import type { ApiError } from "./types";

const API_BASE_URL = "/api/v1";

/**
 * Custom error class for API responses with error codes.
 */
export class ApiRequestError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.code = code;
    this.status = status;
  }
}

/**
 * Build a URL with query parameters, filtering out undefined/null values.
 */
function buildUrl(
  path: string,
  params?: Record<string, string | number | boolean | undefined | null>
): string {
  const url = new URL(`${API_BASE_URL}${path}`, window.location.origin);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.pathname + url.search;
}

/**
 * Generic fetch wrapper with error handling.
 */
async function request<T>(
  path: string,
  options?: RequestInit & {
    params?: Record<string, string | number | boolean | undefined | null>;
  }
): Promise<T> {
  const { params, ...fetchOptions } = options ?? {};
  const url = buildUrl(path, params);

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...fetchOptions.headers,
    },
    credentials: "include",
    ...fetchOptions,
  });

  if (!response.ok) {
    let errorBody: ApiError;
    try {
      errorBody = (await response.json()) as ApiError;
    } catch {
      errorBody = {
        detail: response.statusText || "Unknown error",
        code: "HTTP_ERROR",
      };
    }
    throw new ApiRequestError(
      errorBody.detail,
      errorBody.code,
      response.status
    );
  }

  return response.json() as Promise<T>;
}

/**
 * API client with typed methods for each HTTP verb.
 */
export const apiClient = {
  get<T>(
    path: string,
    params?: Record<string, string | number | boolean | undefined | null>
  ): Promise<T> {
    return request<T>(path, { method: "GET", params });
  },

  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" });
  },
};
