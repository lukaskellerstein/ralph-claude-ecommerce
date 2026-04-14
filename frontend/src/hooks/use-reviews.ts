import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { PaginatedResponse, Review } from "@/lib/types";

interface UseReviewsParams {
  slug: string | undefined;
  pageSize?: number;
}

/**
 * Fetch paginated reviews for a product identified by slug.
 * Uses useInfiniteQuery for cursor-based "Load More" pagination.
 * Reviews are ordered by newest first.
 */
export function useReviews({ slug, pageSize = 10 }: UseReviewsParams) {
  return useInfiniteQuery({
    queryKey: ["reviews", slug, { pageSize }],
    queryFn: ({ pageParam }) =>
      apiClient.get<PaginatedResponse<Review>>(
        `/products/${slug}/reviews`,
        {
          page_size: pageSize,
          after: pageParam ?? undefined,
        }
      ),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_next_page ? lastPage.next_cursor : undefined,
    enabled: !!slug,
  });
}
