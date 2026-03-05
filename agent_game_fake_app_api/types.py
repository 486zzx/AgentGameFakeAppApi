"""
租房仿真 API 类型定义（与需求文档一致）
"""
from typing import Any, Literal, TypedDict

# 挂牌平台
ListingPlatform = Literal["链家", "安居客", "58同城"]

# 地标类别
LandmarkCategory = Literal["subway", "company", "landmark"]

# 小区周边地标类型
NearbyLandmarkType = Literal["shopping", "park"]

# 排序
SortOrder = Literal["asc", "desc"]
HouseSortBy = Literal["price", "area", "subway"]


class ApiResponse(TypedDict, total=False):
    """通用 API 响应外壳"""
    code: int
    message: str
    data: Any


class Landmark(TypedDict, total=False):
    """地标"""
    id: str
    name: str
    category: str
    district: str
    latitude: float
    longitude: float


class LandmarkListData(TypedDict, total=False):
    """地标列表响应"""
    total: int
    items: list[Landmark]


class House(TypedDict, total=False):
    """房源"""
    house_id: str
    id: str
    community: str
    address: str
    district: str
    area: str
    layout: str
    bedrooms: int
    living_rooms: int
    bathrooms: int
    area_sqm: float
    price: int
    rental_type: str
    decoration: str
    orientation: str
    elevator: bool
    subway_station: str
    subway_line: str
    subway_distance: int
    commute_to_xierqi_min: int
    available_from: str
    status: str
    listing_platform: str
    tags: list[str]
    noise_level: str


class HouseNearbyItem(House, total=False):
    """地标附近房源项（含距离信息）"""
    distance_to_landmark: float
    walking_distance: float
    walking_duration: float


class PagedData(TypedDict, total=False):
    """分页列表响应"""
    total: int
    page_size: int
    page: int
    items: list[Any]


class ListingItem(TypedDict, total=False):
    """挂牌记录项"""
    house_id: str
    listing_platform: str


class HouseStats(TypedDict, total=False):
    """房源统计"""
    total: int
    by_status: dict[str, int]
    by_district: dict[str, int]
    price_range: dict[str, int]


class LandmarkStats(TypedDict, total=False):
    """地标统计"""
    total: int
    by_category: dict[str, int]
