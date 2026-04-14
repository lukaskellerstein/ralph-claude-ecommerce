import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Category } from "@/lib/types";

interface CategoryListResponse {
  items: Category[];
}

/**
 * Fetch the full category tree with product counts.
 * Uses a long staleTime since categories change infrequently.
 */
export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => apiClient.get<CategoryListResponse>("/categories"),
    staleTime: 1000 * 60 * 10, // 10 minutes
    select: (data) => data.items,
  });
}
