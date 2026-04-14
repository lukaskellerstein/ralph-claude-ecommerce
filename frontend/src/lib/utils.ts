import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a price in cents to a display string.
 * Example: formatPrice(1999) => "$19.99"
 */
export function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

/**
 * Format a price range for display.
 * Example: formatPriceRange(1000, 5000) => "$10.00 - $50.00"
 */
export function formatPriceRange(minCents: number, maxCents: number): string {
  return `${formatPrice(minCents)} - ${formatPrice(maxCents)}`;
}

/**
 * Truncate a string to a maximum length, adding ellipsis if truncated.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return `${str.slice(0, maxLength)}...`;
}

/**
 * Format a date string for display.
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Generate a placeholder image URL for products without images.
 */
export function getPlaceholderImage(productName: string): string {
  return `https://placehold.co/400x400/e2e8f0/64748b?text=${encodeURIComponent(productName.charAt(0).toUpperCase())}`;
}
