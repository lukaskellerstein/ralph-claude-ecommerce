import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  ChevronRight,
  PackageX,
  ShoppingCart,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ProductGallery } from "@/components/product-gallery";
import { VariantSelector } from "@/components/variant-selector";
import {
  RatingDisplay,
  RatingDistribution,
} from "@/components/rating-display";
import { useProduct } from "@/hooks/use-products";
import { formatPrice } from "@/lib/utils";
import { ApiRequestError } from "@/lib/api-client";

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: product, isLoading, error } = useProduct(slug);
  const [selectedVariantId, setSelectedVariantId] = useState<string | null>(
    null
  );

  // Select the first in-stock variant by default when product loads
  useEffect(() => {
    if (product && product.variants.length > 0 && selectedVariantId === null) {
      const firstInStock = product.variants.find((v) => v.in_stock);
      setSelectedVariantId(firstInStock?.id ?? product.variants[0].id);
    }
  }, [product, selectedVariantId]);

  // SEO meta tags
  useEffect(() => {
    if (product) {
      document.title = `${product.name} | Product Catalog`;

      // Set/update meta description
      let metaDescription = document.querySelector(
        'meta[name="description"]'
      ) as HTMLMetaElement | null;
      if (!metaDescription) {
        metaDescription = document.createElement("meta");
        metaDescription.name = "description";
        document.head.appendChild(metaDescription);
      }
      metaDescription.content = product.description.slice(0, 160);

      // Open Graph tags
      setOrCreateMeta("og:title", product.name);
      setOrCreateMeta("og:description", product.description.slice(0, 160));
      setOrCreateMeta("og:type", "product");
      if (product.images.length > 0) {
        setOrCreateMeta("og:image", product.images[0].url);
      }
    }

    return () => {
      document.title = "Product Catalog";
    };
  }, [product]);

  // Handle 404 error
  if (error) {
    const is404 =
      error instanceof ApiRequestError && error.status === 404;

    if (is404) {
      return <ProductNotFound />;
    }

    return (
      <div className="container mx-auto flex flex-col items-center justify-center px-4 py-16 text-center">
        <p className="text-lg text-destructive">
          Something went wrong while loading this product.
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          {error.message}
        </p>
        <Button asChild variant="outline" className="mt-6">
          <Link to="/products">
            <ArrowLeft className="size-4" />
            Back to catalog
          </Link>
        </Button>
      </div>
    );
  }

  // Loading state
  if (isLoading || !product) {
    return <ProductDetailSkeleton />;
  }

  // Find the selected variant
  const selectedVariant = product.variants.find(
    (v) => v.id === selectedVariantId
  );

  // Resolved price: selected variant price or base price
  const displayPrice = selectedVariant?.price ?? product.base_price;

  // Stock status
  const hasAnyStock = product.variants.some((v) => v.in_stock);
  const isSelectedInStock = selectedVariant?.in_stock ?? hasAnyStock;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6">
        <ol className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <li>
            <Link to="/products" className="hover:text-foreground">
              Products
            </Link>
          </li>
          {product.category.parent && (
            <>
              <ChevronRight className="size-3.5" />
              <li>
                <Link
                  to={`/products?category=${product.category.parent.id}`}
                  className="hover:text-foreground"
                >
                  {product.category.parent.name}
                </Link>
              </li>
            </>
          )}
          <ChevronRight className="size-3.5" />
          <li>
            <Link
              to={`/products?category=${product.category.id}`}
              className="hover:text-foreground"
            >
              {product.category.name}
            </Link>
          </li>
          <ChevronRight className="size-3.5" />
          <li
            className="truncate font-medium text-foreground"
            aria-current="page"
          >
            {product.name}
          </li>
        </ol>
      </nav>

      {/* Main product layout */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Left: Image gallery */}
        <ProductGallery
          images={product.images}
          productName={product.name}
        />

        {/* Right: Product info */}
        <div className="space-y-6">
          {/* Product name */}
          <div>
            <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">
              {product.name}
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {product.category.name}
            </p>
          </div>

          {/* Rating */}
          <RatingDisplay
            averageRating={product.average_rating}
            reviewCount={product.review_count}
            size="md"
          />

          {/* Price */}
          <div className="flex items-baseline gap-3">
            <p className="text-3xl font-bold">
              {formatPrice(displayPrice)}
            </p>
            {selectedVariant &&
              selectedVariant.price !== product.base_price && (
                <p className="text-lg text-muted-foreground line-through">
                  {formatPrice(product.base_price)}
                </p>
              )}
          </div>

          {/* Stock badge */}
          <div>
            {isSelectedInStock ? (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                In Stock
                {selectedVariant && (
                  <span className="ml-1">
                    ({selectedVariant.stock_quantity} available)
                  </span>
                )}
              </Badge>
            ) : (
              <Badge variant="destructive">Out of Stock</Badge>
            )}
          </div>

          {/* Variant selector */}
          {product.variants.length > 0 && (
            <VariantSelector
              variants={product.variants}
              selectedVariantId={selectedVariantId}
              onSelectVariant={setSelectedVariantId}
            />
          )}

          {/* Add to Cart button */}
          <Button
            size="lg"
            className="w-full"
            disabled={!isSelectedInStock}
          >
            <ShoppingCart className="size-5" />
            {isSelectedInStock ? "Add to Cart" : "Out of Stock"}
          </Button>

          {/* Description */}
          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold">Description</h2>
            <div className="mt-3 text-sm leading-relaxed text-muted-foreground whitespace-pre-line">
              {product.description}
            </div>
          </div>
        </div>
      </div>

      {/* Rating distribution section */}
      {product.review_count > 0 && (
        <section className="mt-12 border-t pt-8">
          <h2 className="text-xl font-semibold">Customer Reviews</h2>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <div className="space-y-3">
              <RatingDisplay
                averageRating={product.average_rating}
                reviewCount={product.review_count}
                size="lg"
              />
              <RatingDistribution
                distribution={product.rating_distribution}
                totalReviews={product.review_count}
              />
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

/**
 * Product not found (404) state with a friendly message and link back to catalog.
 */
function ProductNotFound() {
  return (
    <div className="container mx-auto flex flex-col items-center justify-center px-4 py-16 text-center">
      <PackageX className="size-16 text-muted-foreground" />
      <h1 className="mt-6 text-2xl font-bold">Product Not Found</h1>
      <p className="mt-2 max-w-sm text-muted-foreground">
        Sorry, we couldn't find the product you're looking for. It may have been
        removed or the link might be incorrect.
      </p>
      <Button asChild variant="outline" className="mt-6">
        <Link to="/products">
          <ArrowLeft className="size-4" />
          Browse all products
        </Link>
      </Button>
    </div>
  );
}

/**
 * Skeleton loading state for the product detail page.
 */
function ProductDetailSkeleton() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb skeleton */}
      <div className="mb-6 flex items-center gap-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-4" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-4" />
        <Skeleton className="h-4 w-32" />
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Image skeleton */}
        <div className="space-y-3">
          <Skeleton className="aspect-square w-full rounded-lg" />
          <div className="flex gap-2">
            <Skeleton className="size-16 rounded-md" />
            <Skeleton className="size-16 rounded-md" />
            <Skeleton className="size-16 rounded-md" />
          </div>
        </div>

        {/* Info skeleton */}
        <div className="space-y-6">
          <div>
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="mt-2 h-4 w-24" />
          </div>
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-10 w-28" />
          <Skeleton className="h-6 w-20" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-12" />
            <div className="flex gap-2">
              <Skeleton className="h-9 w-16 rounded-md" />
              <Skeleton className="h-9 w-16 rounded-md" />
              <Skeleton className="h-9 w-16 rounded-md" />
            </div>
          </div>
          <Skeleton className="h-11 w-full rounded-md" />
          <div className="space-y-3 border-t pt-6">
            <Skeleton className="h-6 w-28" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Helper: Set or create an Open Graph meta tag.
 */
function setOrCreateMeta(property: string, content: string) {
  let meta = document.querySelector(
    `meta[property="${property}"]`
  ) as HTMLMetaElement | null;
  if (!meta) {
    meta = document.createElement("meta");
    meta.setAttribute("property", property);
    document.head.appendChild(meta);
  }
  meta.content = content;
}
