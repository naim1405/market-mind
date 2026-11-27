import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.core.exceptions.errors import BadRequestError, ConflictError, NotFoundError
from app.modules.customers.models import Customer
from app.modules.customers.repositories import CustomerRepository
from app.modules.orders.models import DeliveryZone, Order, OrderStatus
from app.modules.orders.repositories import OrderRepository
from app.modules.orders.schemas import OrderCreate, OrderUpdate
from app.modules.products.repositories import ProductRepository

# shortcut: same rates for every page, move to per-page settings when shops need their own
DELIVERY_CHARGES = {
    DeliveryZone.INSIDE_DHAKA: Decimal("60.00"),
    DeliveryZone.SUB_DHAKA: Decimal("100.00"),
    DeliveryZone.OUTSIDE_DHAKA: Decimal("120.00"),
}

# match the db's NUMERIC(12, 2) so a fresh order serializes like a reloaded one
CENTS = Decimal("0.01")

ALLOWED_TRANSITIONS = {
    OrderStatus.CONFIRMED: {OrderStatus.BOOKED, OrderStatus.CANCELLED},
    OrderStatus.BOOKED: {OrderStatus.IN_TRANSIT, OrderStatus.CANCELLED},
    OrderStatus.IN_TRANSIT: {OrderStatus.DELIVERED, OrderStatus.RETURNED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.RETURNED: set(),
    OrderStatus.CANCELLED: set(),
}

# statuses where the goods are back on the shelf
STOCK_RESTORING = {OrderStatus.CANCELLED, OrderStatus.RETURNED}


def normalize_phone(phone: str) -> str:
    """+8801712345678 / 8801712345678 / 01712345678 -> 01712345678"""
    return phone.removeprefix("+").removeprefix("88")


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        customer_repo: CustomerRepository,
    ):
        self.order_repo = order_repo
        # needed to price items against the floor and deduct stock
        self.product_repo = product_repo
        # to find or create the customer an order belongs to
        self.customer_repo = customer_repo

    async def create_order(self, page_id: uuid.UUID, data: OrderCreate) -> Order:
        phone = normalize_phone(data.customer_phone)
        customer = await self._get_or_create_customer(page_id, data, phone)

        product_ids = [item.product_id for item in data.items]
        if len(set(product_ids)) != len(product_ids):
            raise BadRequestError("Each product can appear only once; use quantity instead")

        products = {
            p.id: p for p in await self.product_repo.get_products_by_ids(page_id, product_ids)
        }
        if len(products) != len(product_ids):
            raise NotFoundError("Product")

        items = []
        for item in data.items:
            product = products[item.product_id]
            unit_price = item.unit_price if item.unit_price is not None else product.selling_price
            unit_price = Decimal(unit_price).quantize(CENTS)
            if unit_price < product.min_floor_price:
                # don't reveal the floor: this message can reach customers via the AI
                raise BadRequestError(f"Price for {product.name} is below the allowed minimum")
            # any failure raises, and the request rollback undoes earlier deductions
            if not await self.product_repo.deduct_stock(product.id, item.quantity):
                raise BadRequestError(f"Not enough stock for {product.name}")
            items.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                }
            )

        delivery_charge = DELIVERY_CHARGES[data.delivery_zone]
        subtotal = sum(i["unit_price"] * i["quantity"] for i in items)

        return await self.order_repo.create_order(
            {
                "page_id": page_id,
                "customer_id": customer.id,
                "customer_name": data.customer_name,
                "customer_phone": phone,
                "customer_address": data.customer_address,
                "delivery_zone": data.delivery_zone,
                "note": data.note,
                "delivery_charge": delivery_charge,
                "total_amount": subtotal + delivery_charge,
            },
            items,
        )

    async def get_order(self, page_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_order_by_id(order_id)
        if not order or order.page_id != page_id:
            raise NotFoundError("Order")
        return order

    async def list_orders(self, page_id: uuid.UUID, **filters) -> list[Order]:
        return await self.order_repo.list_orders(page_id, **filters)

    async def update_order(
        self, page_id: uuid.UUID, order_id: uuid.UUID, data: OrderUpdate
    ) -> Order:
        order = await self.get_order(page_id, order_id)
        changes = data.model_dump(exclude_unset=True)

        if "customer_phone" in changes:
            changes["customer_phone"] = normalize_phone(changes["customer_phone"])

        new_status = changes.get("status")
        if new_status and new_status != order.status:
            if new_status not in ALLOWED_TRANSITIONS[order.status]:
                raise BadRequestError(f"Cannot change order from {order.status} to {new_status}")
            if new_status == OrderStatus.BOOKED and not changes.get("tracking_id", order.tracking_id):
                raise BadRequestError("A tracking_id is required to book the parcel")
            if new_status in STOCK_RESTORING:
                for item in order.items:
                    if item.product_id:  # product may have been deleted since
                        await self.product_repo.restore_stock(item.product_id, item.quantity)

        try:
            return await self.order_repo.update_order(order, changes)
        except IntegrityError:
            raise ConflictError("Order with this tracking_id")

    async def _get_or_create_customer(
        self, page_id: uuid.UUID, data: OrderCreate, phone: str
    ) -> Customer:
        if data.customer_psid:
            customer = await self.customer_repo.get_customer_by_psid(page_id, data.customer_psid)
        else:
            customer = await self.customer_repo.get_customer_by_phone(page_id, phone)

        details = {"name": data.customer_name, "phone": phone, "address": data.customer_address}
        if customer:
            # keep the latest delivery details as the customer's saved ones
            return await self.customer_repo.update_customer(customer, details)
        return await self.customer_repo.create_customer(
            {"page_id": page_id, "psid": data.customer_psid, **details}
        )
