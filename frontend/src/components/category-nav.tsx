import { ChevronRight, FolderOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Category } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface CategoryNavProps {
  categories: Category[];
  selectedCategoryId: string | null;
  onSelectCategory: (categoryId: string | null) => void;
}

export function CategoryNav({
  categories,
  selectedCategoryId,
  onSelectCategory,
}: CategoryNavProps) {
  return (
    <nav aria-label="Product categories" className="space-y-1">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
        Categories
      </h2>

      {/* "All Products" option */}
      <Button
        variant="ghost"
        className={cn(
          "w-full justify-start gap-2 text-sm font-normal",
          selectedCategoryId === null && "bg-accent font-medium"
        )}
        onClick={() => onSelectCategory(null)}
      >
        <FolderOpen className="size-4" />
        All Products
      </Button>

      {/* Category tree */}
      {categories.map((category) => (
        <CategoryItem
          key={category.id}
          category={category}
          selectedCategoryId={selectedCategoryId}
          onSelectCategory={onSelectCategory}
          depth={0}
        />
      ))}
    </nav>
  );
}

interface CategoryItemProps {
  category: Category;
  selectedCategoryId: string | null;
  onSelectCategory: (categoryId: string | null) => void;
  depth: number;
}

function CategoryItem({
  category,
  selectedCategoryId,
  onSelectCategory,
  depth,
}: CategoryItemProps) {
  const isSelected = selectedCategoryId === category.id;
  const hasChildren = category.children.length > 0;

  return (
    <div>
      <Button
        variant="ghost"
        className={cn(
          "w-full justify-start gap-2 text-sm font-normal",
          isSelected && "bg-accent font-medium",
          depth > 0 && "pl-8"
        )}
        onClick={() => onSelectCategory(category.id)}
      >
        {hasChildren && (
          <ChevronRight className="size-3 text-muted-foreground" />
        )}
        <span className="truncate">{category.name}</span>
        <span className="ml-auto text-xs text-muted-foreground">
          {category.product_count}
        </span>
      </Button>

      {/* Render children */}
      {hasChildren && (
        <div className="ml-2">
          {category.children.map((child) => (
            <CategoryItem
              key={child.id}
              category={child}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={onSelectCategory}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
