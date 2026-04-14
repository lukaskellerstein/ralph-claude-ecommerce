import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

/**
 * Global search bar component with input field, submit handler, and search icon.
 * Reads and syncs with the `q` URL search parameter automatically.
 * Navigates to the products page with the search query as a URL parameter on submit.
 * Accessible from all pages via the layout header.
 */
export function SearchBar() {
  const [searchParams] = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(urlQuery);
  const navigate = useNavigate();

  // Sync local state when URL query changes (e.g., browser back/forward, clear from page)
  useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      navigate(`/products?q=${encodeURIComponent(trimmed)}`);
    } else {
      navigate("/products");
    }
  }

  function handleClear() {
    setQuery("");
    navigate("/products");
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="relative flex w-full max-w-md items-center"
      role="search"
      aria-label="Search products"
    >
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9 pr-8"
          aria-label="Search products"
        />
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-sm p-0.5 text-muted-foreground hover:text-foreground"
            aria-label="Clear search"
          >
            <X className="size-4" />
          </button>
        )}
      </div>
      <Button type="submit" variant="ghost" size="sm" className="ml-2">
        Search
      </Button>
    </form>
  );
}
