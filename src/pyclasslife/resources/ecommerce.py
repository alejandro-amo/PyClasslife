"""eCommerce resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class EcommerceResource(_Resource):
    """Access eCommerce product and transaction endpoints."""

    def list_products(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="ecommerce/products", page=page, limit=limit, params=filters)

    def create_enrollment(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="ecommerce/enrollment", payload=payload)

    def create_admission(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="ecommerce/admission", payload=payload)
