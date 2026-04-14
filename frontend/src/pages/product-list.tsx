import { useSearchParams } from "react-router-dom";
import { PackageSearch, SearchX, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryNav } from "@/components/category-nav";
import { ProductCard } from "@/components/product-card";
import { useCategories } from "@/hooks/use-categories";
import { useProducts } from "@/hooks/use-products";

export function ProductListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryId = searchParams.get("category") ?? null;
  const searchQuery = searchParams.get("q") ?? null;

  // Fetch categories for the sidebar
  const {
    data: categories,
    isLoading: isCategoriesLoading,
  } = useCategories();

  // Fetch products with optional category filter and search query
  const {
    data: productsData,
    isLoading: isProductsLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useProducts({ categoryId, q: searchQuery });

  // Flatten pages into a single product list
  const products = productsData?.pages.flatMap((page) => page.items) ?? [];

  function handleSelectCategory(id: string | null) {
    if (id === null) {
      searchParams.delete("category");
    } else {
      searchParams.set("category", id);
    }
    // Clear search when changing category
    searchParams.delete("q");
    setSearchParams(searchParams, { replace: true });
  }

  function handleClearSearch() {
    searchParams.delete("q");
    setSearchParams(searchParams, { replace: true });
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Sidebar: Category Navigation */}
        <aside className="w-full shrink-0 lg:w-64">
          {isCategoriesLoading ? (
            <CategoryNavSkeleton />
          ) : (
            <CategoryNav
              categories={categories ?? []}
              selectedCategoryId={categoryId}
              onSelectCategory={handleSelectCategory}
            />
          )}
        </aside>

        {/* Main content: Product Grid */}
        <main className="flex-1">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold">{heading}</h1>
            {!isProductsLoading && (
              <p className="mt-1 text-sm text-muted-foreground">
                {products.length} product{products.length !== 1 ? "s" : ""} found
              </p>
            )}
          </div>

          {/* Product Grid */}
          {isProductsLoading ? (
            <ProductGridSkeleton />
          ) : products.length === 0 ? (
            isSearching ? (
              <SearchEmptyState query={searchQuery} onClear={handleClearSearch} />
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
