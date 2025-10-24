from .attachment_router import router as attachment_router
from .category_router import router as category_router
from .label_router import router as label_router
from .public_router import router as public_router
from .test_router import router as test_router
from .ticket_router import router as ticket_router

__all__ = [
    "attachment_router",
    "category_router",
    "label_router",
    "public_router",
    "test_router",
    "ticket_router",
]
