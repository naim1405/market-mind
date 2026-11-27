from app.modules.orders.repositories import OrderRepository
from app.modules.products.repositories import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
    ):
        self.order_repo = order_repo
        # needed to price items against the floor and deduct stock
        self.product_repo = product_repo
