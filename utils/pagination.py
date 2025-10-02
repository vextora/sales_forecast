from typing import List, Any, Generic, TypeVar
from pydantic import BaseModel
from tortoise.queryset import QuerySet

T = TypeVar("T")

class PageMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    meta: PageMeta
    items: List[Any]

async def paginate(queryset: QuerySet, page: int = 1, per_page: int = 10) -> PaginatedResponse:
    """
    Async helper untuk pagination dengan Tortoise ORM.
    queryset: Tortoise QuerySet
    page: halaman ke berapa
    per_page: jumlah item per halaman
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    total = await queryset.count()
    total_pages = (total + per_page - 1) // per_page  # pembulatan ke atas

    offset = (page - 1) * per_page
    items = await queryset.offset(offset).limit(per_page)

    return PaginatedResponse(
        meta=PageMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages
        ),
        items=items
    )