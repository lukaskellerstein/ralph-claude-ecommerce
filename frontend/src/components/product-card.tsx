import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatPrice, getPlaceholderImage } from "@/lib/utils";
import type { ProductListItem } from "@/lib/types";

interface ProductCardProps {
  product: ProductListItem;
}

export function ProductCard({ product }: ProductCardProps) {
  const imageUrl = product.primary_image?.url ?? getPlaceholderImage(product.name);
  const imageAlt = product.primary_image?.alt_text ?? product.name;

  return (
    <Link to={`/products/${product.slug}`} className="group block">
      <Card className="overflow-hidden transition-shadow hover:shadow-md">
        {/* Product image */}
        <div className="relative aspect-square overflow-hidden bg-muted">
          <img
            src={imageUrl}
            alt={imageAlt}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
            loading="lazy"
          />
          {!product.has_stock && (
            <Badge
              variant="destructive"
              className="absolute right-2 top-2"
            >
              Out of Stock
            </Badge>
          )}
        </div>

        <CardContent className="space-y-2 pt-4">
          {/* Category */}
          <p className="text-xs text-muted-foreground">
            {product.category.name}
          </p>

          {/* Product name */}
          <h3 className="line-clamp-2 text-sm font-medium leading-tight group-hover:text-primary">
            {product.name}
          </h3>

          {/* Rating */}
          {product.review_count > 0 && (
            <div className="flex items-center gap-1">
              <Star className="size-3.5 fill-yellow-400 text-yellow-400" />
              <span className="text-xs font-medium">
                {product.average_rating.toFixed(1)}
              </span>
              <span className="text-xs text-muted-foreground">
                ({product.review_count})
              </span>
            </div>
          )}

          {/* Price */}
          <p className="text-base font-semibold">
            {formatPrice(product.base_price)}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
