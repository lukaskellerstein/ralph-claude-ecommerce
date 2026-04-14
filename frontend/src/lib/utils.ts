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
