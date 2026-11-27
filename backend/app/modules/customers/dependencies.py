from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.modules.customers.repositories import CustomerRepository


def get_customer_repository(session: SessionDep) -> CustomerRepository:
    return CustomerRepository(session=session)


CustomerRepositoryDep = Annotated[CustomerRepository, Depends(get_customer_repository)]
