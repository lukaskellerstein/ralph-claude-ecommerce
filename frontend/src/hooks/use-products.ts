import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type {
  PaginatedResponse,
  ProductDetail,
  ProductListItem,
} from "@/lib/types";

interface UseProductsParams {
  categoryId?: string | null;
  q?: string | null;
  pageSize?: number;
}

/**
 * Fetch paginated product list with optional category filter and search query.
 * Uses useInfiniteQuery for cursor-based "Load More" pagination.
 *
 * When `q` is provided, results are ranked by relevance via full-text search.
 * When not provided, results are sorted by newest first.
 */
export function useProducts({
  categoryId,
  q,
  pageSize = 20,
}: UseProductsParams = {}) {
  return useInfiniteQuery({
    queryKey: ["products", { categoryId, q, pageSize }],
    queryFn: ({ pageParam }) =>
      apiClient.get<PaginatedResponse<ProductListItem>>("/products", {
        category_id: categoryId ?? undefined,
        q: q ?? undefined,
        page_size: pageSize,
        after: pageParam ?? undefined,
      }),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_next_page ? lastPage.next_cursor : undefined,
  });
}

/**
 * Fetch a single product by slug for the product detail page.
 * Uses useQuery with the slug as the query key.
 */
export function useProduct(slug: string | undefined) {
  return useQuery({
    queryKey: ["product", slug],
    queryFn: () => apiClient.get<ProductDetail>(`/products/${slug}`),
    enabled: !!slug,
  });
}
