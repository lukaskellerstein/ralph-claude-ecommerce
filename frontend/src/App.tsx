import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Link, Outlet } from "react-router-dom";
import { ShoppingBag } from "lucide-react";
import { ProductListPage } from "@/pages/product-list";
import { ProductDetailPage } from "@/pages/product-detail";
import { SearchBar } from "@/components/search-bar";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

/**
 * Application layout with header containing the SearchBar.
 * The SearchBar is accessible from every page.
 */
function Layout() {
  return (
    <div className="min-h-screen bg-background">
      {/* Global Header */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center gap-4 px-4">
          {/* Logo / Home Link */}
          <Link
            to="/products"
            className="flex shrink-0 items-center gap-2 font-bold text-lg"
          >
            <ShoppingBag className="size-5" />
            <span className="hidden sm:inline">Store</span>
          </Link>

          {/* Search Bar — syncs with URL `q` param automatically */}
          <div className="flex-1 flex justify-center">
            <SearchBar />
          </div>

          {/* Placeholder for future nav items (cart, auth, etc.) */}
          <div className="shrink-0 w-16" />
        </div>
      </header>

      {/* Page Content */}
      <Outlet />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<ProductListPage />} />
            <Route path="/products" element={<ProductListPage />} />
            <Route path="/products/:slug" element={<ProductDetailPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
