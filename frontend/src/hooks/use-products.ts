import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse, ProductListItem } from "@/lib/types";

interface UseProductsParams {
  categoryId?: string | null;
  pageSize?: number;
}

/**
 * Fetch paginated product list with optional category filter.
 * Uses useInfiniteQuery for cursor-based "Load More" pagination.
 */
export function useProducts({
  categoryId,
  pageSize = 20,
}: UseProductsParams = {}) {
  return useInfiniteQuery({
    queryKey: ["products", { categoryId, pageSize }],
    queryFn: ({ pageParam }) =>
      apiClient.get<PaginatedResponse<ProductListItem>>("/products", {
        category_id: categoryId ?? undefined,
        page_size: pageSize,
        after: pageParam ?? undefined,
      }),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_next_page ? lastPage.next_cursor : undefined,
  });
}
