# Eshopy — An Online Store

Eshopy is a full-featured ecommerce web application where customers can browse products, place orders, and pay online, and where store administrators can manage the entire operation from a back-office dashboard.

---

## What the store looks like for a customer

### Finding products

A customer arrives at the storefront and sees products organized into categories (for example, "Electronics > Headphones" or "Clothing > T-Shirts"). Categories can be nested up to two levels deep. A sidebar or top navigation lets the customer drill into any category, with a product count shown next to each one.

A search bar is available on every page. Typing a query searches product names and descriptions and returns results ranked by relevance. If nothing matches, the store shows a friendly "no results" message with suggestions.

On any product listing — whether it's a category page or search results — the customer can narrow things down further by filtering on price range, minimum star rating, and whether the item is in stock. They can sort by price (low to high or high to low), newest arrivals, or most popular. Active filters appear as removable chips, and a single "Clear all" action resets everything. Changing a filter updates the list instantly without a full page reload.

### Product pages

Each product has its own detail page with a gallery of images (thumbnail navigation), a full description, pricing, the category breadcrumb, the average customer rating, and the total number of reviews.

Some products come in variants — different sizes, colors, or configurations. When a variant is selected, the price and stock status update accordingly. An "Add to Cart" button is prominently displayed; if the item is out of stock, the button is disabled.

Below the product details, customers can read reviews left by other buyers. Each review shows the reviewer's name, a star rating, the review text, and the date. A summary at the top breaks down the rating distribution across 1-5 stars. Reviews are paginated so the page stays fast. Authenticated customers who have purchased the product can submit their own review.

### User accounts

Visitors can register with an email address, password, first name, and last name. Passwords must be at least 8 characters with a mix of letters and numbers; a strength indicator gives real-time feedback. After registering, the customer is logged in automatically.

Returning customers log in with their email and password. If they enter wrong credentials five times within fifteen minutes, the account is locked for thirty minutes. A "Forgot password?" link lets them request a reset email; the reset link is valid for one hour and can only be used once.

Once logged in, a customer has an account area with:

- **Profile** — view and edit their name and phone number (email is read-only in v1).
- **Addresses** — save up to five shipping addresses (with a label like "Home" or "Office"), mark one as the default, and edit or delete any of them.
- **Orders** — a full history of past and current orders (see below).
- **Wishlist** — a collection of products they'd like to buy later. A heart icon on any product card or detail page toggles the wishlist. Out-of-stock items stay on the list with a clear label.

The account dashboard at `/account` shows a summary view: the latest order with its status, how many addresses are saved, the wishlist item count, and profile completeness — each linking to the relevant section.

### Shopping and checking out

Customers add products to a cart from the product page (or optionally from listing cards). If the product has variants, a variant must be selected first. Adding the same product again increments the quantity rather than creating a duplicate. The cart icon in the header shows the running item count, and a toast notification confirms each addition.

Guest visitors can also build a cart without logging in. Their cart is stored locally in the browser. When they log in or register, the guest cart merges with any existing server-side cart — if the same item exists in both, the higher quantity wins.

The cart page lists every item with its image, name, variant, unit price, a quantity adjuster (capped at available stock), a line total, and a remove button. A summary shows the subtotal, estimated tax, and total. An empty cart shows a "Continue Shopping" message.

Checkout is a multi-step flow that requires the customer to be logged in (guests are redirected to the login page with a return URL):

1. **Shipping address** — pick a saved address or enter a new one (with the option to save it to the account).
2. **Shipping method** — choose between Standard (5-7 days) and Express (2-3 days), each at a fixed price. The cheapest option is pre-selected.
3. **Payment** — enter card details through a Stripe-powered form. Card data never touches our server. On failure, the customer sees a clear error and can retry.
4. **Confirmation** — a summary of the order: order number, items, shipping address, shipping method, payment breakdown (subtotal, shipping, tax, total), and estimated delivery date. The cart is cleared, and the order immediately appears in order history.

Stock is validated both when an item is added to the cart and again at checkout time. If anything goes out of stock in between, the customer is told which items are affected before they can proceed. Stock is decremented atomically on successful payment so two customers can never buy the last unit of the same item.

### After the purchase

Customers can view their full order history, sorted newest-first. Each order shows its number, date, item count, total, and a color-coded status badge (pending, paid, processing, shipped, delivered, cancelled, or refunded).

Opening an order reveals the full detail: every line item with image and price, the shipping address and method, the payment summary, and a step-by-step status timeline. If the order has shipped, a tracking number is displayed. A "Reorder" button adds all available items from a past order back into the cart.

If an order hasn't shipped yet (status is "paid" or "processing"), the customer can cancel it. Cancellation triggers an automatic refund through Stripe, and the stock for those items is restored.

---

## What the store looks like for an administrator

Admins log in through the same login page as customers. If their account has the admin role, an "Admin" link appears in the header, leading to the admin dashboard at `/admin`. Non-admin users who try to access admin routes see a 403 error.

### Dashboard overview

The admin landing page shows key performance indicators for the last 30 days: total revenue, total orders, average order value, and number of registered customers. A chart plots daily revenue over that period. Below it, the five best-selling products and the five most recent orders are highlighted.

### Managing products

A data table lists every product with a thumbnail, name, category, base price, total stock, and active/inactive status. Admins can search by name, filter by category or status, and sort by name, price, or creation date.

Creating a product means filling in a name (slug is auto-generated but editable), a rich-text description, a category, a base price, and an active/inactive toggle. Multiple images can be uploaded (up to 10 per product, 5 MB each), reordered with drag-and-drop, and given alt text. Variants can be added with their own name (e.g., "Large / Red"), SKU, optional price override, and stock quantity.

Products are never permanently deleted. "Deactivating" a product hides it from the storefront while preserving it in the database and in historical orders.

### Managing categories

Categories are shown as an editable tree. Admins can create root categories or subcategories (max two levels), edit their names, slugs, and parents, and reorder them via drag-and-drop. A category cannot be deleted if products are still assigned to it — the admin is prompted to reassign them first.

### Managing orders

An order management table shows all orders across all customers. Admins can filter by status (multi-select) and date range. Opening an order shows the same information the customer sees, plus the customer's email and an admin-only notes field.

Admins advance orders through their lifecycle: paid to processing, processing to shipped (with a tracking number), shipped to delivered. They can also issue refunds on any paid or completed order. Every status change is logged with the admin's identity and a timestamp.

### Managing users

A user table lists every registered account with email, name, role, registration date, order count, and active status. Admins can promote a customer to admin or demote an admin back to customer (as long as at least one admin always exists). They can also deactivate or reactivate accounts. Deactivated users cannot log in, but their data is preserved. Admins cannot edit another user's profile details — only role and active status.

---

## What is not included in v1

The first version intentionally leaves out the following to keep scope manageable:

- Social or OAuth login (Google, GitHub, etc.)
- Two-factor authentication
- Email verification on registration
- Account deletion or GDPR data export
- Product recommendations ("Customers also bought")
- Product comparison
- Multi-language product descriptions
- Multi-currency support
- Promo codes, coupons, and discounts
- Saved payment methods or digital wallets (Apple Pay, PayPal)
- Subscription or recurring orders
- Order editing after placement
- Real-time tax calculation via a third-party service
- Email notifications for order status changes
- Returns and exchanges
- Invoice or receipt PDF generation
- Customer-admin messaging on orders
- Gift cards and store credit
- Bulk product import/export
- In-browser image cropping or resizing
- Low-stock alerts
- CMS or page content management
- Multi-level admin permissions (all admins have equal access)
