import { useState } from "react";
import { cn, getPlaceholderImage } from "@/lib/utils";
import type { ProductImage } from "@/lib/types";

interface ProductGalleryProps {
  images: ProductImage[];
  productName: string;
}

/**
 * Product image gallery with main display and thumbnail navigation strip.
 * Falls back to a placeholder image when no images are provided.
 */
export function ProductGallery({ images, productName }: ProductGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Sort images by position
  const sortedImages = [...images].sort((a, b) => a.position - b.position);

  // Fallback when no images exist
  if (sortedImages.length === 0) {
    return (
      <div className="space-y-3">
        <div className="aspect-square overflow-hidden rounded-lg bg-muted">
          <img
            src={getPlaceholderImage(productName)}
            alt={productName}
            className="h-full w-full object-cover"
          />
        </div>
      </div>
    );
  }

  const currentImage = sortedImages[selectedIndex];

  return (
    <div className="space-y-3">
      {/* Main image display */}
      <div className="aspect-square overflow-hidden rounded-lg bg-muted">
        <img
          src={currentImage.url}
          alt={currentImage.alt_text || productName}
          className="h-full w-full object-cover"
        />
      </div>

      {/* Thumbnail strip — only show if more than one image */}
      {sortedImages.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {sortedImages.map((image, index) => (
            <button
              key={image.id}
              type="button"
              onClick={() => setSelectedIndex(index)}
              className={cn(
                "relative size-16 shrink-0 overflow-hidden rounded-md border-2 transition-all",
                index === selectedIndex
                  ? "border-primary ring-1 ring-primary"
                  : "border-transparent opacity-70 hover:opacity-100"
              )}
              aria-label={`View image ${index + 1}`}
              aria-current={index === selectedIndex ? "true" : undefined}
            >
              <img
                src={image.url}
                alt={image.alt_text || `${productName} - Image ${index + 1}`}
                className="h-full w-full object-cover"
                loading="lazy"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
