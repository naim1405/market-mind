""" Import all models here """

from app.modules.auth.models import Auth  # noqa: F401
from app.modules.pages.models import Pages  # noqa: F401
from app.modules.users.models import User  # noqa: F401
from app.modules.products.models import Product  # noqa: F401
from app.modules.orders.models import Order, OrderItem  # noqa: F401
from app.modules.customers.models import Customer  # noqa: F401
