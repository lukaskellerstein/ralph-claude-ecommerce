import { useState, useCallback, useEffect } from "react";
import { SlidersHorizontal, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

export interface FilterValues {
  minPrice: number | null;
  maxPrice: number | null;
  minRating: number | null;
  inStock: boolean | null;
}

interface FilterSidebarProps {
  filters: FilterValues;
  onFiltersChange: (filters: FilterValues) => void;
}

/**
 * Sidebar component for filtering products by price range, rating, and stock availability.
 * All monetary values are in cents internally but displayed as dollars to the user.
 */
export function FilterSidebar({ filters, onFiltersChange }: FilterSidebarProps) {
  // Local state for price inputs to allow typing without immediate API calls
  const [localMinPrice, setLocalMinPrice] = useState(
    filters.minPrice !== null ? (filters.minPrice / 100).toString() : ""
  );
  const [localMaxPrice, setLocalMaxPrice] = useState(
    filters.maxPrice !== null ? (filters.maxPrice / 100).toString() : ""
  );

  // Sync local state when filters change externally (e.g., "Clear all")
  useEffect(() => {
    setLocalMinPrice(
      filters.minPrice !== null ? (filters.minPrice / 100).toString() : ""
    );
    setLocalMaxPrice(
      filters.maxPrice !== null ? (filters.maxPrice / 100).toString() : ""
    );
  }, [filters.minPrice, filters.maxPrice]);

  function handlePriceBlur() {
    const min = localMinPrice ? Math.round(parseFloat(localMinPrice) * 100) : null;
    const max = localMaxPrice ? Math.round(parseFloat(localMaxPrice) * 100) : null;

    if (min !== filters.minPrice || max !== filters.maxPrice) {
      onFiltersChange({
        ...filters,
        minPrice: min && !isNaN(min) ? min : null,
        maxPrice: max && !isNaN(max) ? max : null,
      });
    }
  }

  function handlePriceKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      handlePriceBlur();
    }
  }

  function handleRatingChange(rating: number | null) {
    onFiltersChange({ ...filters, minRating: rating });
  }

  function handleInStockChange() {
    onFiltersChange({
      ...filters,
      inStock: filters.inStock ? null : true,
    });
  }

  const hasActiveFilters =
    filters.minPrice !== null ||
    filters.maxPrice !== null ||
    filters.minRating !== null ||
    filters.inStock !== null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          <SlidersHorizontal className="size-4" />
          Filters
        </h3>
      </div>

      {/* Price Range */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Price Range</Label>
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
              $
            </span>
            <Input
              type="number"
              placeholder="Min"
              min={0}
              step={0.01}
              value={localMinPrice}
              onChange={(e) => setLocalMinPrice(e.target.value)}
              onBlur={handlePriceBlur}
              onKeyDown={handlePriceKeyDown}
              className="h-8 pl-6 text-sm"
            />
          </div>
          <span className="text-xs text-muted-foreground">to</span>
          <div className="relative flex-1">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
              $
            </span>
            <Input
              type="number"
              placeholder="Max"
              min={0}
              step={0.01}
              value={localMaxPrice}
              onChange={(e) => setLocalMaxPrice(e.target.value)}
              onBlur={handlePriceBlur}
              onKeyDown={handlePriceKeyDown}
              className="h-8 pl-6 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Rating Filter */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Minimum Rating</Label>
        <div className="flex flex-col gap-1">
          {[4, 3, 2, 1].map((rating) => (
            <button
              key={rating}
              type="button"
              onClick={() =>
                handleRatingChange(
                  filters.minRating === rating ? null : rating
                )
              }
              className={`flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
                filters.minRating === rating
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              <div className="flex items-center">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`size-3.5 ${
                      i < rating
                        ? "fill-amber-400 text-amber-400"
                        : "text-muted-foreground/30"
                    }`}
                  />
                ))}
              </div>
              <span>& up</span>
            </button>
          ))}
        </div>
      </div>

      {/* In Stock Toggle */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Availability</Label>
        <button
          type="button"
          onClick={handleInStockChange}
          className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors ${
            filters.inStock
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <div
            className={`flex size-4 items-center justify-center rounded border transition-colors ${
              filters.inStock
                ? "border-primary bg-primary text-primary-foreground"
                : "border-muted-foreground/30"
            }`}
          >
            {filters.inStock && (
              <svg
                className="size-3"
                viewBox="0 0 12 12"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M2 6L5 9L10 3"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>
          In stock only
        </button>
      </div>
    </div>
  );
}
