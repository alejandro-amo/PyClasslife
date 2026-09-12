"""Finance resource scaffold."""

from ._base import _Resource
from typing import Any, Mapping


class FinanceResource(_Resource):
    """Access receipts, invoices, remittances, providers and discounts."""

    def list_provider_metas(self, *, page: int = 1, limit: int = 500) -> Any:
        return self._get(path="providers/metas")

    def list_provider_teacher_metas(self, *, page: int = 1, limit: int = 500) -> Any:
        return self._get(path="providers/teachers/metas")

    def list_receipts(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="receipts", page=page, limit=limit, params=filters)

    def get_receipt(self, *, receipt_id: str) -> Any:
        return self._get(path=f"receipts/{receipt_id}")

    def list_invoices(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="invoices", page=page, limit=limit, params=filters)

    def get_invoice(self, *, invoice_id: str) -> Any:
        return self._get(path=f"invoices/{invoice_id}")

    def list_remittances(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="remittances", page=page, limit=limit, params=filters)

    def get_remittance(self, *, remittance_id: str) -> Any:
        return self._get(path=f"remittances/{remittance_id}")

    def list_providers(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="providers", page=page, limit=limit, params=filters)

    def get_provider(self, *, provider_id: str) -> Any:
        return self._get(path=f"providers/{provider_id}")

    def update_provider(self, *, provider_id: str, payload: Mapping[str, Any]) -> Any:
        return self._patch(path=f"providers/{provider_id}", payload=payload)

    def list_provider_teachers(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="providers/teachers", page=page, limit=limit, params=filters)

    def get_provider_teacher(self, *, teacher_id: str) -> Any:
        return self._get(path=f"providers/teachers/{teacher_id}")

    def update_provider_teacher(
        self, *, teacher_id: str, payload: Mapping[str, Any]
    ) -> Any:
        return self._patch(path=f"providers/teachers/{teacher_id}", payload=payload)

    def list_discounts(self, *, page: int = 1, limit: int = 500, **filters: Any) -> Any:
        return self._get_page(path="finance/discounts", page=page, limit=limit, params=filters)

    def create_provider(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="providers", payload=payload)

    def create_provider_teacher(self, *, payload: Mapping[str, Any]) -> Any:
        return self._post(path="providers/teachers", payload=payload)

    def delete_provider(self, *, provider_id: str) -> Any:
        return self._delete(path=f"providers/{provider_id}")

    def delete_provider_teacher(self, *, teacher_id: str) -> Any:
        return self._delete(path=f"providers/teachers/{teacher_id}")
