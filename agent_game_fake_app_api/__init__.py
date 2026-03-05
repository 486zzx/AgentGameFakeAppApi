"""
租房仿真 API 客户端，基于需求文档实现的成熟可用组件，供 Agent / 评测脚本使用。
"""
from .client import FakeAppApiClient, create_client_and_init
from .types import (
    ApiResponse,
    House,
    HouseNearbyItem,
    HouseStats,
    Landmark,
    LandmarkCategory,
    LandmarkListData,
    LandmarkStats,
    ListingItem,
    ListingPlatform,
    NearbyLandmarkType,
    PagedData,
    HouseSortBy,
    SortOrder,
)

__all__ = [
    "FakeAppApiClient",
    "create_client_and_init",
    "ApiResponse",
    "House",
    "HouseNearbyItem",
    "HouseStats",
    "Landmark",
    "LandmarkCategory",
    "LandmarkListData",
    "LandmarkStats",
    "ListingItem",
    "ListingPlatform",
    "NearbyLandmarkType",
    "PagedData",
    "HouseSortBy",
    "SortOrder",
]
