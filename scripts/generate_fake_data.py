import csv
import json
import random
import string
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
N_ORDERS = 200
N_TICKETS = 300
RAW_DIR = Path("data/raw")
DOCS_DIR = RAW_DIR / "docs"

STATUSES = ["processing", "shipped", "delivered", "returned", "cancelled"]
PRODUCTS = [("Wireless Mouse", 25.0), ("Mechanical Keyboard", 79.0),
            ("USB-C Hub", 39.0), ("Laptop Stand", 45.0), ("Webcam", 59.0)]

TICKET_TEMPLATES = [
    "Hi, I am {name}. Where is my order #{order_id}? Email me at {email} or call {phone}.",
    "I want to return order #{order_id}. My card {card} was charged twice.",
    "Order #{order_id} arrived damaged. Call me on {phone}. Regards, {name}",
    "Please change the shipping address of order #{order_id} to {address}.",
    "Can I cancel order #{order_id}? My email is {email}.",
    "Is order #{order_id} eligible for a refund? I debugged it with key {api_key}.",
]

DOCS = {
    "return_policy.md": "# Return Policy\n\nItems can be returned within 30 days of delivery.\n"
    "The item must be unused and in original packaging.\n\n"
    "## Damaged items\n\nDamaged items can be returned within 60 days of delivery.\n",
    "shipping_policy.md": "# Shipping Policy\n\nStandard shipping takes 3 to 7 business days.\n"
    "Express shipping takes 1 to 2 business days.\n\n"
    "## Address changes\n\nAddress can be changed only while the order is in processing.\n",
    "refund_policy.md": "# Refund Policy\n\nRefunds are paid to the original payment method.\n"
    "Refunds take 5 to 10 business days after we receive the item.\n",
    "faq.md": "# FAQ\n\n## Can I cancel my order?\n\nYes, only while the order is in processing.\n\n"
    "## How do I track my order?\n\nUse the order id in your confirmation email.\n",
}

def make_orders(fake: Faker)-> list[dict]:
    orders = []
    for i in range(N_ORDERS):
        order_date = fake.date_between(date(2025, 1, 1), date(2025, 12, 31))
        status = random.choice(STATUSES)
        product, price = random.choice(PRODUCTS)
        delivered = status in ("delivered", "returned")
        delivery = order_date + timedelta(days=random.randint(2, 10)) if delivered else None
        orders.append({
            "order_id": 1000 + i,
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "product": product,
            "price": price,
            "status": status,
            "order_date": order_date.isoformat(),
            "delivery_date": delivery.isoformat() if delivery else "",
        })
    return orders

def fake_api_key()-> str:
    return "FAKEKEY-"+ "".join(random.choices(string.ascii_letters + string.digits, k=24))

def make_tickets(fake: Faker, orders: list[dict])-> list[dict]:
    tickets = []
    for i in range(N_TICKETS):
        order = random.choice(orders)
        body = random.choice(TICKET_TEMPLATES).format(
            name=order["customer_name"], email=order["customer_email"],
            phone=fake.phone_number(), card=fake.credit_card_number(),
            address=fake.address().replace("\n", ", "),
            order_id=order["order_id"], api_key=fake_api_key(),
        )
        tickets.append({
            "ticket_id": f"T-{i + 1:04d}",
            "order_id": order["order_id"],
            "created_at": fake.date_between(date(2025, 1, 1), date(2025, 12, 31)).isoformat(),
            "status": random.choice(["open", "solved", "pending"]),
            "body": body,
        })
    return tickets

def main() -> None:
    random.seed(SEED)
    Faker.seed(SEED)
    fake = Faker()

    DOCS_DIR.mkdir(parents = True, exist_ok = True)
    orders = make_orders(fake)
    tickets = make_tickets(fake, orders)

    with open(RAW_DIR / "orders.csv", "w", newline="", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
        writer.writeheader()
        writer.writerows(orders)

    with open(RAW_DIR / "tickets.jsonl", "w", encoding = "utf-8") as f:
        for t in tickets:
            f.write(json.dumps(t, ensure_ascii = False) + "\n")
    for name, text in DOCS.items():
        (DOCS_DIR / name).write_text(text, encoding = "utf-8")

    print(f"orders: {len(orders)}, tickets: {len(tickets)}, docs: {len(DOCS)}")

if __name__=="__main__":
    main()