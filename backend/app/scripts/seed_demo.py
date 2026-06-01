from __future__ import annotations

import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.auth.security import hash_password
from app.core.config import get_settings
from app.models import AuditLog, Customer, Order, OrderItem, Product, User
from app.schemas.orders import OrderCreate, OrderItemCreate
from app.services.orders import create_order


DEMO_ADMIN_EMAIL = "admin@stockroomdemo.com"


@dataclass(frozen=True)
class ProductSeed:
    name: str
    sku: str
    description: str
    category: str


@dataclass(frozen=True)
class CustomerSeed:
    name: str
    email: str
    company: str
    phone: str


PRODUCTS: list[ProductSeed] = [
    ProductSeed("UltraDock Pro", "DOCK-1001", "Thunderbolt docking station with dual 4K output", "Workspace"),
    ProductSeed("PeakView 27 Monitor", "MON-1002", "27-inch QHD monitor with USB-C power delivery", "Display"),
    ProductSeed("GridKey Mechanical Keyboard", "KB-1003", "Hot-swappable keyboard with tactile switches", "Peripherals"),
    ProductSeed("Signal Mouse Pro", "MSE-1004", "Wireless ergonomic mouse with programmable buttons", "Peripherals"),
    ProductSeed("NorthStar WiFi 6 Router", "NET-1005", "Business-grade router for small office networks", "Networking"),
    ProductSeed("CloudVault SSD 1TB", "SSD-1006", "Portable NVMe SSD with hardware encryption", "Storage"),
    ProductSeed("CloudVault SSD 2TB", "SSD-1007", "Portable NVMe SSD with hardware encryption", "Storage"),
    ProductSeed("Pulse Headset", "AUD-1008", "Noise-cancelling headset for support teams", "Audio"),
    ProductSeed("Pulse Webcam", "CAM-1009", "1080p webcam with low-light correction", "Audio"),
    ProductSeed("Volt USB-C Hub", "HUB-1010", "7-port USB-C hub with SD card support", "Accessories"),
    ProductSeed("Volt USB-C Hub Mini", "HUB-1011", "Compact 4-port travel hub", "Accessories"),
    ProductSeed("Atlas Laptop Stand", "ACC-1012", "Aluminum stand with adjustable tilt", "Workspace"),
    ProductSeed("Atlas Desk Mat", "ACC-1013", "Large stitched desk mat for daily use", "Workspace"),
    ProductSeed("Switchback Ethernet Cable", "NET-1014", "Cat6 cable in 2m, 5m, and 10m runs", "Networking"),
    ProductSeed("Switchback Patch Kit", "NET-1015", "Assorted patch cables and cable ties", "Networking"),
    ProductSeed("Beacon Label Printer", "PRN-1016", "Thermal label printer for warehouse workflows", "Operations"),
    ProductSeed("Beacon Spare Rolls", "PRN-1017", "Pack of thermal label rolls", "Operations"),
    ProductSeed("Relay Barcode Scanner", "SCN-1018", "Handheld scanner for receiving and shipping", "Operations"),
    ProductSeed("Relay Scanner Dock", "SCN-1019", "Charging cradle for Relay scanners", "Operations"),
    ProductSeed("Harbor Surge Protector", "PWR-1020", "8-outlet surge strip with USB charging", "Power"),
    ProductSeed("Harbor UPS Mini", "PWR-1021", "Compact battery backup for essential equipment", "Power"),
    ProductSeed("Summit Laptop 13", "LTP-1022", "Lightweight laptop with 13-inch display", "Computing"),
    ProductSeed("Summit Laptop 15", "LTP-1023", "Performance laptop with 15-inch display", "Computing"),
    ProductSeed("Summit Charger 65W", "PWR-1024", "USB-C fast charger for laptops and tablets", "Power"),
    ProductSeed("Summit Charger 100W", "PWR-1025", "High-output charger for multi-device setups", "Power"),
    ProductSeed("Luma LED Desk Lamp", "LMP-1026", "Dimmable desk lamp with warm and cool modes", "Workspace"),
    ProductSeed("Luma Replacement Bulb", "LMP-1027", "Spare bulb pack for Luma lamp systems", "Workspace"),
    ProductSeed("Trace Cable Sleeves", "ACC-1028", "Reusable cable sleeves, pack of 10", "Accessories"),
    ProductSeed("Trace Cable Labels", "ACC-1029", "Color-coded adhesive labels for cable runs", "Accessories"),
    ProductSeed("Echo Speaker Bar", "AUD-1030", "Compact speaker bar for meeting rooms", "Audio"),
    ProductSeed("Echo Conference Mic", "AUD-1031", "Boundary microphone for group calls", "Audio"),
    ProductSeed("Nimbus Tablet Stand", "ACC-1032", "Adjustable stand for tablets and terminals", "Workspace"),
    ProductSeed("Nimbus Stylus", "ACC-1033", "Precision stylus for field teams", "Workspace"),
    ProductSeed("Circuit Test Kit", "TST-1034", "Portable kit for cable and port diagnostics", "Operations"),
    ProductSeed("Circuit Replacement Tips", "TST-1035", "Replacement probes and tips for the test kit", "Operations"),
    ProductSeed("Vector Label Roll", "LBL-1036", "High-contrast label roll for printers", "Operations"),
    ProductSeed("Vector Label Sleeves", "LBL-1037", "Protective sleeves for shipping labels", "Operations"),
    ProductSeed("Drift Dock Cable", "DOCK-1038", "Replacement cable for docking station", "Workspace"),
    ProductSeed("Drift Power Brick", "PWR-1039", "Replacement power brick for workstation devices", "Power"),
    ProductSeed("Studio Ring Light", "LGT-1040", "Adjustable ring light for video calls", "Audio"),
]

CUSTOMERS: list[CustomerSeed] = [
    CustomerSeed("Northwind Logistics", "purchasing@northwindlogistics.com", "Northwind Logistics", "+1-212-555-0101"),
    CustomerSeed("Aster Retail", "ops@asterretail.com", "Aster Retail", "+1-415-555-0102"),
    CustomerSeed("Bluebird Studio", "hello@bluebirdstudio.com", "Bluebird Studio", "+1-646-555-0103"),
    CustomerSeed("Harbor Clinic", "office@harborclinic.com", "Harbor Clinic", "+1-312-555-0104"),
    CustomerSeed("Summit Foods", "procurement@summitfoods.com", "Summit Foods", "+1-206-555-0105"),
    CustomerSeed("Pixel Works", "finance@pixelworks.com", "Pixel Works", "+1-917-555-0106"),
    CustomerSeed("Copper Freight", "orders@copperfreight.com", "Copper Freight", "+1-213-555-0107"),
    CustomerSeed("Mosaic Agency", "accounts@mosaicagency.com", "Mosaic Agency", "+1-404-555-0108"),
    CustomerSeed("Northbay Hardware", "purchasing@northbayhardware.com", "Northbay Hardware", "+1-510-555-0109"),
    CustomerSeed("Orbit Labs", "ops@orbitlabs.com", "Orbit Labs", "+1-617-555-0110"),
    CustomerSeed("Cedar & Co", "buying@cedarandco.com", "Cedar & Co", "+1-312-555-0111"),
    CustomerSeed("Brightline Dental", "admin@brightlinedental.com", "Brightline Dental", "+1-702-555-0112"),
    CustomerSeed("Fieldstone Group", "purchasing@fieldstonegroup.com", "Fieldstone Group", "+1-503-555-0113"),
    CustomerSeed("Daybreak School", "operations@daybreakschool.edu", "Daybreak School", "+1-303-555-0114"),
    CustomerSeed("Golden Thread", "finance@goldenthread.com", "Golden Thread", "+1-617-555-0115"),
    CustomerSeed("Harborline Cafe", "owner@harborlinecafe.com", "Harborline Cafe", "+1-206-555-0116"),
    CustomerSeed("Juniper Studios", "studio@juniperstudios.com", "Juniper Studios", "+1-646-555-0117"),
    CustomerSeed("Keystone Dental", "admin@keystonedental.com", "Keystone Dental", "+1-215-555-0118"),
    CustomerSeed("Lattice Architecture", "procurement@latticearch.com", "Lattice Architecture", "+1-312-555-0119"),
    CustomerSeed("Metro Freight", "ops@metrofreight.com", "Metro Freight", "+1-212-555-0120"),
    CustomerSeed("Nova Fitness", "billing@novafitness.com", "Nova Fitness", "+1-510-555-0121"),
    CustomerSeed("Oak & Alloy", "purchasing@oakandalloy.com", "Oak & Alloy", "+1-415-555-0122"),
    CustomerSeed("Pine District Office", "admin@pinedistrictoffice.org", "Pine District Office", "+1-303-555-0123"),
    CustomerSeed("Quarry Supply", "orders@quarrysupply.com", "Quarry Supply", "+1-404-555-0124"),
    CustomerSeed("Redwood Health", "finance@redwoodhealth.com", "Redwood Health", "+1-415-555-0125"),
    CustomerSeed("Stonebridge Finance", "ops@stonebridgefinance.com", "Stonebridge Finance", "+1-646-555-0126"),
    CustomerSeed("Tidewater Markets", "buying@tidewatermarkets.com", "Tidewater Markets", "+1-213-555-0127"),
    CustomerSeed("Union Studio", "office@unionstudio.com", "Union Studio", "+1-617-555-0128"),
    CustomerSeed("Vista Consulting", "procurement@vistaconsulting.com", "Vista Consulting", "+1-503-555-0129"),
    CustomerSeed("Westend Medical", "admin@westendmedical.com", "Westend Medical", "+1-312-555-0130"),
    CustomerSeed("Yellow Brick Retail", "sales@yellowbrickretail.com", "Yellow Brick Retail", "+1-702-555-0131"),
    CustomerSeed("Zenith Products", "ops@zenithproducts.com", "Zenith Products", "+1-206-555-0132"),
    CustomerSeed("Atlas Home Goods", "purchasing@atlashomegoods.com", "Atlas Home Goods", "+1-510-555-0133"),
    CustomerSeed("Briar & Bloom", "accounts@briarbloom.com", "Briar & Bloom", "+1-212-555-0134"),
    CustomerSeed("Crane Studio", "hello@cranestudio.com", "Crane Studio", "+1-617-555-0135"),
    CustomerSeed("Delta Learning", "billing@deltalearning.org", "Delta Learning", "+1-303-555-0136"),
    CustomerSeed("Elm Logistics", "ops@elmlogistics.com", "Elm Logistics", "+1-404-555-0137"),
    CustomerSeed("Focal Point Media", "procurement@focalpointmedia.com", "Focal Point Media", "+1-415-555-0138"),
    CustomerSeed("Granite Builders", "office@granitebuilders.com", "Granite Builders", "+1-312-555-0139"),
    CustomerSeed("Horizon Events", "finance@horizonevents.com", "Horizon Events", "+1-646-555-0140"),
]


def make_engine():
    database_url = os.getenv("DATABASE_URL") or get_settings().database_url
    return create_engine(database_url, pool_pre_ping=True)


def ensure_admin_user(session: Session, now: datetime) -> User:
    user = session.execute(select(User).where(User.email == DEMO_ADMIN_EMAIL)).scalar_one_or_none()
    if user:
        return user
    user = User(
        name="Stockroom Admin",
        email=DEMO_ADMIN_EMAIL,
        password_hash=hash_password("Stockroom123!"),
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    session.flush()
    return user


def product_quantity(product_index: int, rng: random.Random) -> int:
    base = 18 + (product_index % 6) * 11
    return base + rng.randint(12, 96)


def product_price(product_index: int, rng: random.Random) -> Decimal:
    price = Decimal("12.50") + Decimal((product_index % 8) * 9) + Decimal(rng.randint(0, 220)) / Decimal("10")
    return price.quantize(Decimal("0.01"))


def customer_created_at(index: int, now: datetime) -> datetime:
    return now - timedelta(days=180 - index * 3)


def product_created_at(index: int, now: datetime) -> datetime:
    return now - timedelta(days=220 - index * 2)


def order_date(index: int, now: datetime, rng: random.Random) -> datetime:
    return now - timedelta(days=rng.randint(1, 150), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))


def seed_products(session: Session, now: datetime, rng: random.Random) -> list[Product]:
    products: list[Product] = []
    for index, item in enumerate(PRODUCTS, start=1):
        existing = session.execute(select(Product).where(Product.sku == item.sku)).scalar_one_or_none()
        if existing:
            products.append(existing)
            continue
        product = Product(
            name=item.name,
            sku=item.sku,
            description=f"{item.description} ({item.category})",
            unit_price=product_price(index, rng),
            quantity=product_quantity(index, rng),
            low_stock_threshold=5 + (index % 6) * 2,
            created_at=product_created_at(index, now),
            updated_at=product_created_at(index, now),
        )
        session.add(product)
        session.flush()
        session.add(AuditLog(entity_type="product", entity_id=product.id, action="created", user_id=None, created_at=product.created_at))
        products.append(product)
    return products


def seed_customers(session: Session, now: datetime) -> list[Customer]:
    customers: list[Customer] = []
    for index, item in enumerate(CUSTOMERS, start=1):
        existing = session.execute(select(Customer).where(Customer.email == item.email)).scalar_one_or_none()
        if existing:
            customers.append(existing)
            continue
        customer = Customer(
            name=item.name,
            email=item.email,
            company=item.company,
            phone=item.phone,
            created_at=customer_created_at(index, now),
            updated_at=customer_created_at(index, now),
        )
        session.add(customer)
        session.flush()
        session.add(AuditLog(entity_type="customer", entity_id=customer.id, action="created", user_id=None, created_at=customer.created_at))
        customers.append(customer)
    return customers


def seed_orders(session: Session, user: User, products: list[Product], customers: list[Customer], now: datetime, rng: random.Random) -> None:
    existing_count = session.query(Order).count()
    if existing_count >= 90:
        return

    orders_to_create = 90 - existing_count
    seed_offset = existing_count
    for order_index in range(orders_to_create):
        customer = rng.choice(customers)
        line_count = rng.randint(1, 4)
        chosen_products = rng.sample(products, k=line_count)
        payload = OrderCreate(
            customer_id=customer.id,
            items=[
                OrderItemCreate(
                    product_id=product.id,
                    quantity=rng.randint(1, 3),
                )
                for product in chosen_products
            ],
        )
        response, _ = create_order(
            session,
            payload,
            user,
            idempotency_key=f"seed-{seed_offset + order_index}",
        )
        order = session.get(Order, response["id"])
        if order is None:
            raise RuntimeError("Seed order was not persisted")
        created_at = order_date(order_index, now, rng)
        order.created_at = created_at
        order.updated_at = created_at
        if order_index % 12 == 0:
            order.status = "cancelled"
            order.deleted_at = created_at + timedelta(days=7)
            for item in order.items:
                item.product.quantity += item.quantity
            session.add(
                AuditLog(
                    entity_type="order",
                    entity_id=order.id,
                    action="cancelled",
                    user_id=user.id,
                    created_at=created_at + timedelta(days=7),
                )
            )
        session.commit()


def seed_demo_data() -> None:
    engine = make_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        existing_marker = session.execute(select(User).where(User.email == DEMO_ADMIN_EMAIL)).scalar_one_or_none()
        if existing_marker and session.query(Product).count() >= len(PRODUCTS) and session.query(Customer).count() >= len(CUSTOMERS) and session.query(Order).count() >= 90:
            return
        user = ensure_admin_user(session, now)
        session.commit()

        products = seed_products(session, now, rng)
        customers = seed_customers(session, now)
        session.commit()

        seed_orders(session, user, products, customers, now, rng)


def main() -> None:
    seed_demo_data()


if __name__ == "__main__":
    main()
