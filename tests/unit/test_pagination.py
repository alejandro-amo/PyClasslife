import pytest

from pyclasslife import Page, Pagination


def test_page_exposes_navigation_metadata() -> None:
    page = Page(total=4808, page=2, limit=100, count=100, items=[])
    assert page.total_pages == 49
    assert page.has_previous is True
    assert page.has_next is True
    assert page.previous_page == 1
    assert page.next_page == 3


def test_page_handles_empty_collection() -> None:
    page = Page(total=0, page=1, limit=500, count=0, items=[])
    assert page.total_pages == 0
    assert page.has_previous is False
    assert page.has_next is False
    assert page.previous_page is None
    assert page.next_page is None


def test_page_handles_last_page() -> None:
    page = Page(total=4808, page=49, limit=100, count=8, items=[])
    assert page.total_pages == 49
    assert page.has_next is False
    assert page.next_page is None


@pytest.mark.parametrize("field", ["page", "limit"])
def test_pagination_rejects_non_positive_values(field: str) -> None:
    values = {"page": 1, "limit": 500}
    values[field] = 0
    with pytest.raises(ValueError):
        Pagination(**values)
