import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type {
  PaginatedResponse,
  ProductDetail,
  ProductListItem,
  SortOption,
} from "@/lib/types";

interface UseProductsParams {
  categoryId?: string | null;
  q?: string | null;
  minPrice?: number | null;
  maxPrice?: number | null;
  minRating?: number | null;
  inStock?: boolean | null;
  sort?: SortOption;
  pageSize?: number;
}

/**
 * Fetch paginated product list with optional category filter, search query,
 * price/rating/stock filters, and sort order.
 * Uses useInfiniteQuery for cursor-based "Load More" pagination.
 *
 * When `q` is provided, results are ranked by relevance via full-text search (sort ignored).
 * When not provided, results are sorted by the chosen sort option (default: newest).
 */
export function useProducts({
  categoryId,
  q,
  minPrice,
  maxPrice,
  minRating,
  inStock,
  sort = "newest",
  pageSize = 20,
}: UseProductsParams = {}) {
  return useInfiniteQuery({
    queryKey: [
      "products",
      { categoryId, q, minPrice, maxPrice, minRating, inStock, sort, pageSize },
    ],
    queryFn: ({ pageParam }) =>
      apiClient.get<PaginatedResponse<ProductListItem>>("/products", {
        category_id: categoryId ?? undefined,
        q: q ?? undefined,
        min_price: minPrice ?? undefined,
        max_price: maxPrice ?? undefined,
        min_rating: minRating ?? undefined,
        in_stock: inStock ?? undefined,
        sort: sort,
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
