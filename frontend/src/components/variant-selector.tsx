import { cn } from "@/lib/utils";
import type { ProductVariant } from "@/lib/types";

interface VariantSelectorProps {
  variants: ProductVariant[];
  selectedVariantId: string | null;
  onSelectVariant: (variantId: string) => void;
}

/**
 * Grouped variant selector with active selection state, price/stock feedback,
 * and out-of-stock disabled state.
 *
 * Groups variants by variant_type (e.g., "Size", "Color") and displays
 * each group with selectable option buttons.
 */
export function VariantSelector({
  variants,
  selectedVariantId,
  onSelectVariant,
}: VariantSelectorProps) {
  if (variants.length === 0) {
    return null;
  }

  // Group variants by type
  const groups = new Map<string, ProductVariant[]>();
  for (const variant of variants) {
    const existing = groups.get(variant.variant_type) ?? [];
    existing.push(variant);
    groups.set(variant.variant_type, existing);
  }

  return (
    <div className="space-y-4">
      {Array.from(groups.entries()).map(([type, typeVariants]) => (
        <div key={type} className="space-y-2">
          <label className="text-sm font-medium text-foreground">
            {type}
          </label>
          <div className="flex flex-wrap gap-2">
            {typeVariants.map((variant) => {
              const isSelected = variant.id === selectedVariantId;
              const isOutOfStock = !variant.in_stock;

              return (
                <button
                  key={variant.id}
                  type="button"
                  onClick={() => onSelectVariant(variant.id)}
                  disabled={isOutOfStock}
                  className={cn(
                    "rounded-md border px-3 py-1.5 text-sm font-medium transition-all",
                    isSelected
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background hover:border-primary/50",
                    isOutOfStock &&
                      "cursor-not-allowed border-border bg-muted text-muted-foreground line-through opacity-50"
                  )}
                  aria-label={`${type}: ${variant.variant_value}${isOutOfStock ? " (out of stock)" : ""}`}
                  aria-pressed={isSelected}
                >
                  {variant.variant_value}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
