import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface RatingDisplayProps {
  averageRating: number;
  reviewCount: number;
  size?: "sm" | "md" | "lg";
}

/**
 * Star rating display showing the average score as filled/empty stars
 * along with the numeric average and review count.
 */
export function RatingDisplay({
  averageRating,
  reviewCount,
  size = "md",
}: RatingDisplayProps) {
  if (reviewCount === 0) {
    return (
      <p className="text-sm text-muted-foreground">No reviews yet</p>
    );
  }

  const sizeClasses = {
    sm: "size-3.5",
    md: "size-4",
    lg: "size-5",
  };

  const textClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  };

  return (
    <div className="flex items-center gap-1.5">
      {/* Star icons */}
      <div className="flex items-center gap-0.5" aria-label={`${averageRating.toFixed(1)} out of 5 stars`}>
        {Array.from({ length: 5 }, (_, i) => {
          const starValue = i + 1;
          const isFull = averageRating >= starValue;
          const isHalf = !isFull && averageRating >= starValue - 0.5;

          return (
            <Star
              key={i}
              className={cn(
                sizeClasses[size],
                isFull || isHalf
                  ? "fill-yellow-400 text-yellow-400"
                  : "fill-none text-muted-foreground/40"
              )}
            />
          );
        })}
      </div>

      {/* Numeric average */}
      <span className={cn("font-medium", textClasses[size])}>
        {averageRating.toFixed(1)}
      </span>

      {/* Review count */}
      <span className={cn("text-muted-foreground", textClasses[size])}>
        ({reviewCount} {reviewCount === 1 ? "review" : "reviews"})
      </span>
    </div>
  );
}

interface RatingDistributionProps {
  distribution: Record<string, number>;
  totalReviews: number;
}

/**
 * Bar chart showing the distribution of star ratings (1-5) alongside
 * the total review count and average.
 */
export function RatingDistribution({
  distribution,
  totalReviews,
}: RatingDistributionProps) {
  if (totalReviews === 0) {
    return null;
  }

  return (
    <div className="space-y-1.5">
      {[5, 4, 3, 2, 1].map((star) => {
        const count = distribution[String(star)] ?? 0;
        const percentage = totalReviews > 0 ? (count / totalReviews) * 100 : 0;

        return (
          <div key={star} className="flex items-center gap-2 text-sm">
            <span className="w-8 text-right text-muted-foreground">
              {star} ★
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-yellow-400 transition-all"
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="w-8 text-right text-xs text-muted-foreground">
              {count}
            </span>
          </div>
        );
      })}
    </div>
  );
}
