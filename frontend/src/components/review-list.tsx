import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/lib/utils";
import { useReviews } from "@/hooks/use-reviews";

interface ReviewListProps {
  slug: string;
}

/**
 * Paginated review list displaying individual reviews with
 * reviewer name, star rating, review text, and date.
 * Includes a "Load more" button for cursor-based pagination.
 */
export function ReviewList({ slug }: ReviewListProps) {
  const {
    data,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useReviews({ slug, pageSize: 10 });

  if (isLoading) {
    return <ReviewListSkeleton />;
  }

  const reviews = data?.pages.flatMap((page) => page.items) ?? [];

  if (reviews.length === 0) {
    return (
      <p className="py-8 text-center text-muted-foreground">
        No reviews yet. Be the first to leave a review!
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {reviews.map((review) => (
        <article
          key={review.id}
          className="border-b pb-6 last:border-b-0 last:pb-0"
        >
          {/* Header: name + date */}
          <div className="flex items-center justify-between">
            <p className="font-medium">{review.reviewer_name}</p>
            <time
              className="text-sm text-muted-foreground"
              dateTime={review.created_at}
            >
              {formatDate(review.created_at)}
            </time>
          </div>

          {/* Star rating */}
          <div
            className="mt-1 flex items-center gap-0.5"
            aria-label={`${review.rating} out of 5 stars`}
          >
            {Array.from({ length: 5 }, (_, i) => (
              <Star
                key={i}
                className={`size-4 ${
                  i < review.rating
                    ? "fill-yellow-400 text-yellow-400"
                    : "fill-none text-muted-foreground/40"
                }`}
              />
            ))}
          </div>

          {/* Review text */}
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {review.text}
          </p>
        </article>
      ))}

      {/* Load more button */}
      {hasNextPage && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? "Loading..." : "Load more reviews"}
          </Button>
        </div>
      )}
    </div>
  );
}

/**
 * Skeleton loading state for the review list.
 */
function ReviewListSkeleton() {
  return (
    <div className="space-y-6">
      {Array.from({ length: 3 }, (_, i) => (
        <div key={i} className="border-b pb-6 last:border-b-0 last:pb-0">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-28" />
            <Skeleton className="h-4 w-24" />
          </div>
          <div className="mt-1 flex gap-0.5">
            {Array.from({ length: 5 }, (_, j) => (
              <Skeleton key={j} className="size-4 rounded-full" />
            ))}
          </div>
          <Skeleton className="mt-2 h-4 w-full" />
          <Skeleton className="mt-1 h-4 w-3/4" />
        </div>
      ))}
    </div>
  );
}
