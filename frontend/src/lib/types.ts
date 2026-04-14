// ==========================================
// Shared TypeScript types for the e-commerce app
// All monetary values are in cents (integers)
// ==========================================

// --- Pagination ---

export interface PaginatedResponse<T> {
  items: T[];
  next_cursor: string | null;
  has_next_page: boolean;
}

// --- Category ---

export interface Category {
  id: string;
  name: string;
  slug: string;
  product_count: number;
  children: Category[];
}

export interface CategoryRef {
  id: string;
  name: string;
  slug: string;
}

export interface CategoryWithParent extends CategoryRef {
  parent: CategoryRef | null;
}

// --- Product Image ---

export interface ProductImage {
  id: string;
  url: string;
  alt_text: string;
  position: number;
}

// --- Product Variant ---

export interface ProductVariant {
  id: string;
  variant_type: string;
  variant_value: string;
  sku: string;
  price: number; // Resolved price in cents (price_override or base_price)
  stock_quantity: number;
  in_stock: boolean;
}

// --- Product (List Item) ---

export interface ProductListItem {
  id: string;
  name: string;
  slug: string;
  description: string;
  base_price: number; // cents
  category: CategoryRef;
  primary_image: ProductImage | null;
  average_rating: number;
  review_count: number;
  has_stock: boolean;
}

// --- Product (Detail) ---

export interface ProductDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  base_price: number; // cents
  category: CategoryWithParent;
  images: ProductImage[];
  variants: ProductVariant[];
  average_rating: number;
  review_count: number;
  rating_distribution: Record<string, number>;
  created_at: string;
}

// --- Review ---

export interface Review {
  id: string;
  rating: number;
  text: string;
  reviewer_name: string;
  created_at: string;
  updated_at?: string;
}

// --- API Error ---

export interface ApiError {
  detail: string;
  code: string;
}

// --- Filter/Sort ---

export type SortOption =
  | "price_asc"
  | "price_desc"
  | "newest"
  | "popular";

export interface ProductFilters {
  category_id?: string;
  q?: string;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  in_stock?: boolean;
  sort?: SortOption;
}
