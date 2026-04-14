import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { PackageSearch, SearchX, Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryNav } from "@/components/category-nav";
import { ProductCard } from "@/components/product-card";
import { FilterSidebar, type FilterValues } from "@/components/filter-sidebar";
import { SortSelect } from "@/components/sort-select";
import { useCategories } from "@/hooks/use-categories";
import { useProducts } from "@/hooks/use-products";
import { formatPrice } from "@/lib/utils";
import type { SortOption } from "@/lib/types";

/**
 * Parse filter/sort state from URL search params.
 * All monetary values are stored in cents in the URL (matching the API).
 */
function parseFiltersFromParams(params: URLSearchParams): FilterValues {
  const minPrice = params.get("min_price");
  const maxPrice = params.get("max_price");
  const minRating = params.get("min_rating");
  const inStock = params.get("in_stock");

  return {
    minPrice: minPrice ? parseInt(minPrice, 10) : null,
    maxPrice: maxPrice ? parseInt(maxPrice, 10) : null,
    minRating: minRating ? parseInt(minRating, 10) : null,
    inStock: inStock === "true" ? true : null,
  };
}

function parseSortFromParams(params: URLSearchParams): SortOption {
  const sort = params.get("sort");
  if (
    sort === "price_asc" ||
    sort === "price_desc" ||
    sort === "newest" ||
    sort === "popular"
  ) {
    return sort;
  }
  return "newest";
}

export function ProductListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryId = searchParams.get("category") ?? null;
  const searchQuery = searchParams.get("q") ?? null;

  // Parse filter and sort state from URL
  const filters = parseFiltersFromParams(searchParams);
  const sort = parseSortFromParams(searchParams);

  // Fetch categories for the sidebar
  const {
    data: categories,
    isLoading: isCategoriesLoading,
  } = useCategories();

  // Fetch products with all params synced from URL
  const {
    data: productsData,
    isLoading: isProductsLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useProducts({
    categoryId,
    q: searchQuery,
    minPrice: filters.minPrice,
    maxPrice: filters.maxPrice,
    minRating: filters.minRating,
    inStock: filters.inStock,
    sort,
  });

  // Flatten pages into a single product list
  const products = productsData?.pages.flatMap((page) => page.items) ?? [];

  // --- URL State Handlers (no page reload, replaces URL params) ---

  function handleSelectCategory(id: string | null) {
    const next = new URLSearchParams(searchParams);
    if (id === null) {
      next.delete("category");
    } else {
      next.set("category", id);
    }
    // Clear search when changing category
    next.delete("q");
    setSearchParams(next, { replace: true });
  }

  function handleClearSearch() {
    const next = new URLSearchParams(searchParams);
    next.delete("q");
    setSearchParams(next, { replace: true });
  }

  const handleFiltersChange = useCallback(
    (newFilters: FilterValues) => {
      const next = new URLSearchParams(searchParams);

      // Update or remove each filter param
      if (newFilters.minPrice !== null) {
        next.set("min_price", String(newFilters.minPrice));
      } else {
        next.delete("min_price");
      }

      if (newFilters.maxPrice !== null) {
        next.set("max_price", String(newFilters.maxPrice));
      } else {
        next.delete("max_price");
      }

      if (newFilters.minRating !== null) {
        next.set("min_rating", String(newFilters.minRating));
      } else {
        next.delete("min_rating");
      }

      if (newFilters.inStock !== null) {
        next.set("in_stock", "true");
      } else {
        next.delete("in_stock");
      }

      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const handleSortChange = useCallback(
    (newSort: SortOption) => {
      const next = new URLSearchParams(searchParams);
      if (newSort === "newest") {
        // Default sort — remove from URL for cleanliness
        next.delete("sort");
      } else {
        next.set("sort", newSort);
      }
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  function handleClearAllFilters() {
    const next = new URLSearchParams(searchParams);
    next.delete("min_price");
    next.delete("max_price");
    next.delete("min_rating");
    next.delete("in_stock");
    next.delete("sort");
    setSearchParams(next, { replace: true });
  }

  function handleRemoveFilter(key: string) {
    const next = new URLSearchParams(searchParams);
    next.delete(key);
    setSearchParams(next, { replace: true });
  }

  // Find the currently selected category name for display
  const selectedCategoryName = categoryId
    ? findCategoryName(categories ?? [], categoryId)
    : null;

  // Determine the page heading
  const isSearching = searchQuery !== null && searchQuery.trim() !== "";
  const heading = isSearching
    ? `Search results for "${searchQuery}"`
    : selectedCategoryName ?? "All Products";

  // Build active filter chips
  const activeFilterChips = buildActiveFilterChips(filters, sort);
  const hasActiveFilters = activeFilterChips.length > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Sidebar: Category Navigation + Filters */}
        <aside className="w-full shrink-0 lg:w-64">
          <div className="space-y-8">
            {isCategoriesLoading ? (
              <CategoryNavSkeleton />
            ) : (
              <CategoryNav
                categories={categories ?? []}
                selectedCategoryId={categoryId}
                onSelectCategory={handleSelectCategory}
              />
            )}

            {/* Filter Sidebar */}
            <FilterSidebar
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
          </div>
        </aside>

        {/* Main content: Product Grid */}
        <main className="flex-1">
          {/* Header with Sort */}
          <div className="mb-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-2xl font-bold">{heading}</h1>
                {!isProductsLoading && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    {products.length} product{products.length !== 1 ? "s" : ""} found
                  </p>
                )}
              </div>
              <SortSelect value={sort} onChange={handleSortChange} />
            </div>

            {/* Active Filter Chips */}
            {hasActiveFilters && (
              <div className="mt-4 flex flex-wrap items-center gap-2">
                {activeFilterChips.map((chip) => (
                  <Badge
                    key={chip.key}
                    variant="secondary"
                    className="flex items-center gap-1 cursor-pointer hover:bg-secondary/80"
                    onClick={() => handleRemoveFilter(chip.key)}
                  >
                    {chip.label}
                    <X className="size-3" />
                  </Badge>
                ))}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs text-muted-foreground"
                  onClick={handleClearAllFilters}
                >
                  Clear all
                </Button>
              </div>
            )}
          </div>

          {/* Product Grid */}
          {isProductsLoading ? (
            <ProductGridSkeleton />
          ) : products.length === 0 ? (
            isSearching ? (
              <SearchEmptyState query={searchQuery} onClear={handleClearSearch} />
            ) : hasActiveFilters ? (
              <FilterEmptyState onClear={handleClearAllFilters} />
            ) : (
              <EmptyState categoryName={selectedCategoryName} />
            )
          ) : (
            <>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Load More */}
              {hasNextPage && (
                <div className="mt-8 flex justify-center">
                  <Button
                    variant="outline"
                    onClick={() => fetchNextPage()}
                    disabled={isFetchingNextPage}
                  >
                    {isFetchingNextPage ? (
                      <>
                        <Loader2 className="size-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      "Load More"
                    )}
                  </Button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

/**
 * Build a list of active filter chips for display.
 * Each chip has a key (URL param name) and a human-readable label.
 */
function buildActiveFilterChips(
  filters: FilterValues,
  sort: SortOption
): { key: string; label: string }[] {
  const chips: { key: string; label: string }[] = [];

  if (filters.minPrice !== null) {
    chips.push({
      key: "min_price",
      label: `Min: ${formatPrice(filters.minPrice)}`,
    });
  }
  if (filters.maxPrice !== null) {
    chips.push({
      key: "max_price",
      label: `Max: ${formatPrice(filters.maxPrice)}`,
    });
  }
  if (filters.minRating !== null) {
    chips.push({
      key: "min_rating",
      label: `${filters.minRating}+ stars`,
    });
  }
  if (filters.inStock !== null) {
    chips.push({
      key: "in_stock",
      label: "In stock",
    });
  }
  if (sort !== "newest") {
    const sortLabels: Record<string, string> = {
      price_asc: "Price: Low to High",
      price_desc: "Price: High to Low",
      popular: "Most Popular",
    };
    chips.push({
      key: "sort",
      label: `Sort: ${sortLabels[sort] ?? sort}`,
    });
  }

  return chips;
}

/**
 * Empty state when no products match the current filters.
 */
function FilterEmptyState({ onClear }: { onClear: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <PackageSearch className="size-12 text-muted-foreground" />
      <h2 className="mt-4 text-lg font-semibold">No products match your filters</h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        Try adjusting or removing some filters to see more products.
      </p>
      <Button variant="outline" className="mt-6" onClick={onClear}>
        Clear all filters
      </Button>
    </div>
  );
}

/**
 * Find a category name by ID in a nested category tree.
 */
function findCategoryName(
  categories: { id: string; name: string; children: { id: string; name: string; children: unknown[] }[] }[],
  id: string
): string | null {
  for (const cat of categories) {
    if (cat.id === id) return cat.name;
    for (const child of cat.children) {
      if (child.id === id) return child.name;
    }
  }
  return null;
}

/**
 * Skeleton loading state for category navigation.
 */
function CategoryNavSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-9 w-full" />
      <Skeleton className="h-9 w-full" />
      <Skeleton className="h-9 w-full" />
      <Skeleton className="h-9 w-3/4 ml-4" />
      <Skeleton className="h-9 w-3/4 ml-4" />
      <Skeleton className="h-9 w-full" />
      <Skeleton className="h-9 w-full" />
    </div>
  );
}

/**
 * Skeleton loading state for the product grid.
 */
function ProductGridSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="space-y-3">
          <Skeleton className="aspect-square w-full rounded-xl" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-5 w-20" />
        </div>
      ))}
    </div>
  );
}

/**
 * Empty state when no products match the current filter (non-search).
 */
function EmptyState({ categoryName }: { categoryName: string | null }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <PackageSearch className="size-12 text-muted-foreground" />
      <h2 className="mt-4 text-lg font-semibold">No products found</h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        {categoryName
          ? `There are no products in the "${categoryName}" category yet.`
          : "There are no products in the catalog yet."}
      </p>
    </div>
  );
}

/**
 * Friendly empty state for search results with suggestions.
 */
function SearchEmptyState({
  query,
  onClear,
}: {
  query: string;
  onClear: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <SearchX className="size-12 text-muted-foreground" />
      <h2 className="mt-4 text-lg font-semibold">
        No results for &ldquo;{query}&rdquo;
      </h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        We couldn&apos;t find any products matching your search. Try using different
        keywords, checking for typos, or browsing our categories.
      </p>
      <Button variant="outline" className="mt-6" onClick={onClear}>
        Clear search
      </Button>
    </div>
  );
}
