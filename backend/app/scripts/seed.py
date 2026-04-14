"""Seed script to populate the database with sample data.

Run with: python -m app.scripts.seed
"""

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.category import Category
from app.models.product import Product, ProductImage, ProductVariant
from app.models.review import Review

# Image base URL
IMG = "https://images.unsplash.com/photo-"


async def seed_categories(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Create sample categories (2 levels deep)."""
    categories: dict[str, uuid.UUID] = {}

    # Root categories
    root_data = [
        ("Electronics", "electronics", 0),
        ("Clothing", "clothing", 1),
        ("Home & Garden", "home-garden", 2),
        ("Sports & Outdoors", "sports-outdoors", 3),
    ]

    root_cats: list[Category] = []
    for name, slug, position in root_data:
        cat = Category(name=name, slug=slug, position=position)
        session.add(cat)
        root_cats.append(cat)

    await session.flush()
    for cat in root_cats:
        categories[cat.slug] = cat.id

    # Child categories
    children_data = [
        ("Laptops", "laptops", categories["electronics"], 0),
        ("Phones", "phones", categories["electronics"], 1),
        ("Audio", "audio", categories["electronics"], 2),
        ("Men's Wear", "mens-wear", categories["clothing"], 0),
        ("Women's Wear", "womens-wear", categories["clothing"], 1),
        ("Accessories", "accessories", categories["clothing"], 2),
        ("Furniture", "furniture", categories["home-garden"], 0),
        ("Kitchen", "kitchen", categories["home-garden"], 1),
        ("Fitness", "fitness", categories["sports-outdoors"], 0),
        ("Camping", "camping", categories["sports-outdoors"], 1),
    ]

    child_cats: list[Category] = []
    for name, slug, parent_id, position in children_data:
        cat = Category(
            name=name, slug=slug, parent_id=parent_id, position=position
        )
        session.add(cat)
        child_cats.append(cat)

    await session.flush()
    for cat in child_cats:
        categories[cat.slug] = cat.id

    return categories


async def seed_products(
    session: AsyncSession,
    categories: dict[str, uuid.UUID],
) -> list[Product]:
    """Create sample products with images and variants."""
    products_data = [
        {
            "name": "ProBook Ultra 15",
            "slug": "probook-ultra-15",
            "description": (
                "A powerful 15-inch laptop with the latest processor, "
                "16GB RAM, and a stunning 4K display. Perfect for "
                "professionals and creators who need performance."
            ),
            "base_price": 129999,
            "category": "laptops",
            "images": [
                (f"{IMG}1496181133206-80ce9b88a853?w=800", "Front view", 0),
                (f"{IMG}1525547719571-a2d4ac8945e2?w=800", "Side view", 1),
            ],
            "variants": [
                ("Storage", "256GB SSD", "PBU15-256", None, 15),
                ("Storage", "512GB SSD", "PBU15-512", 149999, 10),
                ("Storage", "1TB SSD", "PBU15-1TB", 169999, 5),
            ],
        },
        {
            "name": "SwiftPhone 14 Pro",
            "slug": "swiftphone-14-pro",
            "description": (
                "The ultimate smartphone with a 6.7-inch OLED display, "
                "triple camera system with 200MP sensor, 5G connectivity, "
                "and all-day battery life."
            ),
            "base_price": 99999,
            "category": "phones",
            "images": [
                (f"{IMG}1511707171634-5f897ff02aa9?w=800", "Front", 0),
                (f"{IMG}1592899677977-9c10ca588bbd?w=800", "Back", 1),
            ],
            "variants": [
                ("Color", "Midnight Black", "SP14P-BLK", None, 20),
                ("Color", "Silver Frost", "SP14P-SIL", None, 15),
                ("Color", "Ocean Blue", "SP14P-BLU", None, 8),
                ("Storage", "128GB", "SP14P-128", None, 25),
                ("Storage", "256GB", "SP14P-256", 109999, 12),
            ],
        },
        {
            "name": "SoundWave Pro Headphones",
            "slug": "soundwave-pro-headphones",
            "description": (
                "Premium wireless over-ear headphones with active noise "
                "cancellation, 40-hour battery life, and studio-quality "
                "sound. Features Bluetooth 5.3 and multipoint."
            ),
            "base_price": 34999,
            "category": "audio",
            "images": [
                (f"{IMG}1505740420928-5e560c06d30e?w=800", "Headphones", 0),
            ],
            "variants": [
                ("Color", "Charcoal", "SWP-CHA", None, 30),
                ("Color", "Ivory", "SWP-IVY", None, 20),
                ("Color", "Navy", "SWP-NAV", None, 15),
            ],
        },
        {
            "name": "Classic Oxford Shirt",
            "slug": "classic-oxford-shirt",
            "description": (
                "A timeless button-down oxford shirt made from premium "
                "100% cotton. Features a relaxed fit, single chest pocket, "
                "and classic collar. Perfect for business casual."
            ),
            "base_price": 6999,
            "category": "mens-wear",
            "images": [
                (f"{IMG}1596755094514-f87e34085b2c?w=800", "Front", 0),
            ],
            "variants": [
                ("Size", "S", "COS-S", None, 25),
                ("Size", "M", "COS-M", None, 40),
                ("Size", "L", "COS-L", None, 35),
                ("Size", "XL", "COS-XL", None, 20),
                ("Color", "White", "COS-WHT", None, 50),
                ("Color", "Light Blue", "COS-LBL", None, 35),
                ("Color", "Pink", "COS-PNK", None, 25),
            ],
        },
        {
            "name": "Silk Midi Dress",
            "slug": "silk-midi-dress",
            "description": (
                "An elegant silk midi dress with a flattering A-line "
                "silhouette. Features a V-neckline, adjustable waist tie, "
                "and flowy skirt. Ideal for special occasions."
            ),
            "base_price": 14999,
            "category": "womens-wear",
            "images": [
                (f"{IMG}1595777457583-95e059d581b8?w=800", "Front", 0),
                (f"{IMG}1572804013309-59a88b7e92f1?w=800", "Detail", 1),
            ],
            "variants": [
                ("Size", "XS", "SMD-XS", None, 10),
                ("Size", "S", "SMD-S", None, 15),
                ("Size", "M", "SMD-M", None, 20),
                ("Size", "L", "SMD-L", None, 12),
                ("Color", "Black", "SMD-BLK", None, 30),
                ("Color", "Emerald", "SMD-EMR", None, 15),
                ("Color", "Burgundy", "SMD-BRG", None, 12),
            ],
        },
        {
            "name": "Leather Crossbody Bag",
            "slug": "leather-crossbody-bag",
            "description": (
                "Handcrafted genuine leather crossbody bag with adjustable "
                "strap, multiple compartments, and magnetic closure. "
                "Compact yet spacious enough for everyday essentials."
            ),
            "base_price": 8999,
            "category": "accessories",
            "images": [
                (f"{IMG}1548036328-c9fa89d128fa?w=800", "Crossbody Bag", 0),
            ],
            "variants": [
                ("Color", "Tan", "LCB-TAN", None, 18),
                ("Color", "Black", "LCB-BLK", None, 22),
                ("Color", "Cognac", "LCB-COG", None, 14),
            ],
        },
        {
            "name": "Ergonomic Office Chair",
            "slug": "ergonomic-office-chair",
            "description": (
                "A fully adjustable ergonomic office chair with lumbar "
                "support, breathable mesh back, adjustable armrests, and "
                "seat height control. Designed for 8+ hours of sitting."
            ),
            "base_price": 49999,
            "category": "furniture",
            "images": [
                (f"{IMG}1580480055273-228ff5388ef8?w=800", "Office Chair", 0),
            ],
            "variants": [
                ("Color", "Black", "EOC-BLK", None, 15),
                ("Color", "Gray", "EOC-GRY", None, 10),
            ],
        },
        {
            "name": "Cast Iron Dutch Oven",
            "slug": "cast-iron-dutch-oven",
            "description": (
                "Heavy-duty enameled cast iron Dutch oven with a 6-quart "
                "capacity. Perfect for soups, stews, roasts, and bread "
                "baking. Oven-safe up to 500F with a self-basting lid."
            ),
            "base_price": 7999,
            "category": "kitchen",
            "images": [
                (f"{IMG}1585442433867-e2a5da411153?w=800", "Dutch Oven", 0),
            ],
            "variants": [
                ("Color", "Cherry Red", "CIDO-RED", None, 20),
                ("Color", "Matte Black", "CIDO-BLK", None, 25),
                ("Color", "Marine Blue", "CIDO-BLU", None, 12),
                ("Size", "4 Qt", "CIDO-4Q", 5999, 15),
                ("Size", "6 Qt", "CIDO-6Q", None, 20),
                ("Size", "8 Qt", "CIDO-8Q", 9999, 8),
            ],
        },
        {
            "name": "Adjustable Dumbbell Set",
            "slug": "adjustable-dumbbell-set",
            "description": (
                "Space-saving adjustable dumbbell set that replaces 15 "
                "sets of weights. Each dumbbell adjusts from 5 to 52.5 "
                "lbs with a quick-turn dial. Includes a storage tray."
            ),
            "base_price": 39999,
            "category": "fitness",
            "images": [
                (f"{IMG}1534438327276-14e5300c3a48?w=800", "Dumbbell Set", 0),
            ],
            "variants": [
                ("Weight Range", "5-25 lbs", "ADS-25", 24999, 20),
                ("Weight Range", "5-52.5 lbs", "ADS-52", None, 15),
            ],
        },
        {
            "name": "Ultralight Camping Tent",
            "slug": "ultralight-camping-tent",
            "description": (
                "A 2-person ultralight backpacking tent weighing just "
                "3.5 lbs. Features waterproof ripstop nylon, dual "
                "vestibules, easy setup, and excellent ventilation."
            ),
            "base_price": 29999,
            "category": "camping",
            "images": [
                (f"{IMG}1504280390367-361c6d9f38f4?w=800", "Camping Tent", 0),
            ],
            "variants": [
                ("Capacity", "2-Person", "UCT-2P", None, 12),
                ("Capacity", "3-Person", "UCT-3P", 34999, 8),
            ],
        },
        {
            "name": "Wireless Earbuds Sport",
            "slug": "wireless-earbuds-sport",
            "description": (
                "IPX7 waterproof wireless earbuds designed for active "
                "lifestyles. Features secure-fit ear hooks, 10-hour "
                "battery, ANC mode, and transparency mode."
            ),
            "base_price": 14999,
            "category": "audio",
            "images": [
                (f"{IMG}1590658268037-6bf12f032f55?w=800", "Earbuds", 0),
            ],
            "variants": [
                ("Color", "Black", "WES-BLK", None, 40),
                ("Color", "White", "WES-WHT", None, 25),
                ("Color", "Red", "WES-RED", None, 15),
            ],
        },
        {
            "name": "Premium Yoga Mat",
            "slug": "premium-yoga-mat",
            "description": (
                "Extra-thick 6mm yoga mat made from eco-friendly natural "
                "rubber with a microfiber suede surface. Non-slip grip "
                "improves with moisture. Includes carrying strap."
            ),
            "base_price": 7999,
            "category": "fitness",
            "images": [
                (f"{IMG}1601925260368-ae2f83cf8b7f?w=800", "Yoga Mat", 0),
            ],
            "variants": [
                ("Color", "Sage Green", "PYM-GRN", None, 20),
                ("Color", "Dusty Rose", "PYM-RSE", None, 15),
                ("Color", "Midnight Blue", "PYM-BLU", None, 18),
            ],
        },
    ]

    products: list[Product] = []

    for data in products_data:
        product = Product(
            name=data["name"],
            slug=data["slug"],
            description=data["description"],
            base_price=data["base_price"],
            category_id=categories[data["category"]],
        )
        session.add(product)
        await session.flush()

        # Add images
        for url, alt_text, position in data["images"]:
            image = ProductImage(
                product_id=product.id,
                url=url,
                alt_text=alt_text,
                position=position,
            )
            session.add(image)

        # Add variants
        for vtype, vvalue, sku, price, stock in data["variants"]:
            variant = ProductVariant(
                product_id=product.id,
                variant_type=vtype,
                variant_value=vvalue,
                sku=sku,
                price_override=price,
                stock_quantity=stock,
            )
            session.add(variant)

        products.append(product)

    await session.flush()
    return products


async def seed_reviews(
    session: AsyncSession,
    products: list[Product],
) -> int:
    """Create sample reviews for products."""
    # Generate deterministic user UUIDs for seed data
    seed_users = [
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567801"), "Alice Johnson"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567802"), "Bob Smith"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567803"), "Carol White"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567804"), "David Brown"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567805"), "Eve Martinez"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567806"), "Frank Lee"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567807"), "Grace Kim"),
        (uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567808"), "Henry Davis"),
    ]

    # Reviews mapped by product slug
    reviews_data: dict[str, list[tuple[int, int, str]]] = {
        # (user_index, rating, text)
        "probook-ultra-15": [
            (0, 5, "Incredible performance! The 4K display is stunning and the processor handles everything I throw at it. Best laptop I've owned."),
            (1, 4, "Great build quality and performance. Only wish the battery lasted a bit longer under heavy workloads. The display is gorgeous though."),
            (2, 5, "Perfect for my design work. Fast, beautiful screen, and the keyboard is comfortable for long sessions."),
            (3, 4, "Solid laptop for the price. Handles video editing smoothly. The fan can get a bit loud under sustained load."),
            (4, 3, "Good laptop overall but runs hot during intensive tasks. Performance is great when it's not thermal throttling."),
        ],
        "swiftphone-14-pro": [
            (0, 5, "The camera system is unbelievable. Night photos look like daylight. Battery easily lasts all day. Love this phone."),
            (1, 5, "Upgraded from the 12 and the difference is night and day. The OLED display is the best I've seen on any phone."),
            (2, 4, "Fantastic phone. The 200MP camera takes incredible detail shots. Only minor complaint is the weight."),
            (3, 4, "Great phone, fast 5G, amazing display. Wish it came with a charger in the box though."),
            (5, 5, "Best smartphone I've ever used. The triple camera system is versatile and the battery life is outstanding."),
            (6, 3, "Good phone but expensive. The camera is excellent but I'm not sure it justifies the premium over the standard model."),
        ],
        "soundwave-pro-headphones": [
            (0, 5, "The noise cancellation is phenomenal. I use these on flights and in the office. 40 hours of battery is not an exaggeration."),
            (2, 4, "Excellent sound quality and comfortable for long listening sessions. The ANC is top-tier."),
            (4, 5, "Studio-quality sound wasn't an overstatement. These are my daily drivers now. Multipoint is seamless."),
            (6, 4, "Very comfortable and great sound. The carrying case is a nice touch. Bluetooth 5.3 connectivity is rock solid."),
        ],
        "classic-oxford-shirt": [
            (1, 5, "Perfect fit and excellent quality cotton. The relaxed fit is comfortable without being too baggy. Ordered three more."),
            (3, 4, "Nice shirt for the price. Fabric is soft and breathable. Holds up well after multiple washes."),
            (5, 5, "Best oxford shirt I've found. The collar roll is perfect and the fabric gets better with each wash."),
            (7, 3, "Good quality but runs a bit large. I'd recommend sizing down. The light blue color is beautiful."),
        ],
        "silk-midi-dress": [
            (0, 5, "Absolutely stunning dress. The silk quality is luxurious and the A-line cut is incredibly flattering."),
            (2, 5, "Wore this to a wedding and got so many compliments. The adjustable waist tie is a thoughtful detail."),
            (4, 4, "Beautiful dress. The emerald color is even better in person. Only note: it wrinkles easily so hang it up."),
        ],
        "ergonomic-office-chair": [
            (1, 5, "Game changer for working from home. My back pain disappeared after switching to this chair. Worth every penny."),
            (3, 4, "Very comfortable for long work days. The lumbar support is adjustable which is great. Assembly took about 30 minutes."),
            (5, 5, "Best office chair I've owned. The mesh back keeps you cool and the armrests are actually useful."),
            (7, 4, "Solid chair. The adjustability is impressive. Only wish the seat cushion was a bit softer."),
        ],
        "cast-iron-dutch-oven": [
            (0, 5, "Makes incredible soups and bread. The heat distribution is perfectly even. This will last a lifetime."),
            (2, 5, "Heavy but worth it. My sourdough bread has never been better. The enamel coating makes cleanup easy."),
            (4, 4, "Excellent Dutch oven. The cherry red color looks beautiful on the table. Handles large roasts with ease."),
            (6, 5, "Restaurant quality results at home. I use it almost daily. The self-basting lid is genius."),
            (7, 4, "Great quality cast iron. It's heavy but that's expected. Heats evenly and retains heat well."),
        ],
        "adjustable-dumbbell-set": [
            (1, 5, "Replaced my entire dumbbell rack. The dial mechanism is smooth and quick. Perfect for home workouts."),
            (3, 4, "Great space saver. The weight increments are convenient. The storage tray keeps things organized."),
            (5, 4, "Good quality adjustable dumbbells. The range from 5-52.5 lbs covers all my exercises. Smooth transitions."),
        ],
        "premium-yoga-mat": [
            (0, 5, "The grip gets better when you sweat - perfect for hot yoga. The thickness provides great cushioning."),
            (2, 4, "Love the eco-friendly materials. The sage green color is calming. Carrying strap is convenient."),
            (4, 5, "Best yoga mat I've ever used. Non-slip surface is incredible. Worth the investment."),
            (6, 4, "Nice thick mat with good grip. The natural rubber smell fades after a few uses. Very durable."),
        ],
    }

    review_count = 0
    product_map = {p.slug: p for p in products}

    for product_slug, product_reviews in reviews_data.items():
        product = product_map.get(product_slug)
        if product is None:
            continue

        for user_index, rating, review_text in product_reviews:
            user_id, _ = seed_users[user_index]
            review = Review(
                product_id=product.id,
                user_id=user_id,
                rating=rating,
                text=review_text,
            )
            session.add(review)
            review_count += 1

    await session.flush()
    return review_count


async def clear_data(session: AsyncSession) -> None:
    """Clear all existing seed data."""
    await session.execute(text("DELETE FROM reviews"))
    await session.execute(text("DELETE FROM product_variants"))
    await session.execute(text("DELETE FROM product_images"))
    await session.execute(text("DELETE FROM products"))
    await session.execute(text("DELETE FROM categories"))
    await session.flush()


async def seed() -> None:
    """Main seed function."""
    print("Seeding database...")

    async with async_session_factory() as session:
        async with session.begin():
            # Clear existing data
            print("  Clearing existing data...")
            await clear_data(session)

            # Seed categories
            print("  Creating categories...")
            categories = await seed_categories(session)
            print(f"    Created {len(categories)} categories")

            # Seed products
            print("  Creating products with images and variants...")
            products = await seed_products(session, categories)
            print(f"    Created {len(products)} products")

            # Seed reviews
            print("  Creating reviews...")
            review_count = await seed_reviews(session, products)
            print(f"    Created {review_count} reviews")

    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
