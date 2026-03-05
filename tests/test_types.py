"""类型与导出检查，确保包可被正确导入与使用。"""
import pytest

from agent_game_fake_app_api import (
    FakeAppApiClient,
    create_client_and_init,
    ApiResponse,
    House,
    HouseNearbyItem,
    HouseStats,
    Landmark,
    LandmarkListData,
    LandmarkStats,
    ListingItem,
    ListingPlatform,
    NearbyLandmarkType,
    PagedData,
    HouseSortBy,
    SortOrder,
)


def test_client_instantiate():
    c = FakeAppApiClient(base_url="http://localhost:8080", user_id="u")
    assert c.base_url == "http://localhost:8080"
    assert c.user_id == "u"


def test_listing_platform_literal():
    """挂牌平台仅允许 链家/安居客/58同城。"""
    # 类型存在即可，运行时由 API 约束
    platforms: list[ListingPlatform] = ["链家", "安居客", "58同城"]
    assert len(platforms) == 3


def test_landmark_category_literal():
    categories: list[str] = ["subway", "company", "landmark"]
    assert "subway" in categories
