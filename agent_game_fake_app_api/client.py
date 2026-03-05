"""
租房仿真 API 客户端
- 房源相关接口自动附加 X-User-ID
- 支持配置 base_url、user_id，便于 Agent 与评测使用
"""
from typing import Any, Optional
from urllib.parse import urlencode, urljoin

import requests

from .types import (
    ApiResponse,
    LandmarkCategory,
    ListingPlatform,
    NearbyLandmarkType,
    HouseSortBy,
    SortOrder,
)

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 10000


class FakeAppApiClient:
    """租房仿真 API 客户端"""

    def __init__(
        self,
        base_url: str,
        user_id: str,
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
    ):
        """
        Args:
            base_url: 接口基地址，如 http://IP:8080
            user_id: 用户工号，房源接口必传；地标接口不需要
            session: 可选，自定义 requests.Session（如需要代理、重试）
            timeout: 请求超时秒数
        """
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self._session = session or requests.Session()
        self.timeout = timeout

    def _url(self, path: str, params: Optional[dict[str, Any]] = None) -> str:
        path = path if path.startswith("/") else f"/{path}"
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        if params:
            query = urlencode({k: v for k, v in params.items() if v is not None and v != ""})
            url = f"{url}?{query}" if query else url
        return url

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        need_user_id: bool = False,
        **kwargs: Any,
    ) -> ApiResponse:
        url = self._url(path, params)
        headers = dict(kwargs.pop("headers", {}))
        if need_user_id:
            headers["X-User-ID"] = self.user_id
        resp = self._session.request(
            method,
            url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json()

    # ---------- 房源数据重置（建议每新 session 调用一次） ----------
    def init_houses(self) -> ApiResponse:
        """重置当前用户视角下的房源数据状态。建议每新起一个 session 调用一次。"""
        return self._request("POST", "/api/houses/init", need_user_id=True)

    # ---------- 地标接口（不需 X-User-ID） ----------
    def get_landmarks(
        self,
        category: Optional[LandmarkCategory] = None,
        district: Optional[str] = None,
    ) -> ApiResponse:
        """获取地标列表，支持 category、district 同时筛选（取交集）。"""
        params: dict[str, Any] = {}
        if category is not None:
            params["category"] = category
        if district is not None:
            params["district"] = district
        return self._request("GET", "/api/landmarks", params=params or None)

    def get_landmark_by_name(self, name: str) -> ApiResponse:
        """按名称精确查询地标，如西二旗站、百度。"""
        path = f"/api/landmarks/name/{name}"
        return self._request("GET", path)

    def search_landmarks(
        self,
        q: str,
        category: Optional[LandmarkCategory] = None,
        district: Optional[str] = None,
    ) -> ApiResponse:
        """关键词模糊搜索地标，q 必填。"""
        params: dict[str, Any] = {"q": q}
        if category is not None:
            params["category"] = category
        if district is not None:
            params["district"] = district
        return self._request("GET", "/api/landmarks/search", params=params)

    def get_landmark_by_id(self, id: str) -> ApiResponse:
        """按地标 id 查询地标详情。"""
        path = f"/api/landmarks/{id}"
        return self._request("GET", path)

    def get_landmark_stats(self) -> ApiResponse:
        """获取地标统计信息（总数、按类别分布等）。"""
        return self._request("GET", "/api/landmarks/stats")

    # ---------- 房源接口（需 X-User-ID） ----------
    def get_house(self, house_id: str) -> ApiResponse:
        """根据房源 ID 获取单套房源详情。"""
        path = f"/api/houses/{house_id}"
        return self._request("GET", path, need_user_id=True)

    def get_house_listings(self, house_id: str) -> ApiResponse:
        """根据房源 ID 获取各平台挂牌记录。"""
        path = f"/api/houses/listings/{house_id}"
        return self._request("GET", path, need_user_id=True)

    def get_houses_by_community(
        self,
        community: str,
        listing_platform: Optional[ListingPlatform] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> ApiResponse:
        """按小区名查询该小区下可租房源。"""
        params: dict[str, Any] = {"community": community}
        if listing_platform is not None:
            params["listing_platform"] = listing_platform
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = min(page_size, MAX_PAGE_SIZE)
        return self._request("GET", "/api/houses/by_community", params=params, need_user_id=True)

    def get_houses_by_platform(
        self,
        listing_platform: Optional[ListingPlatform] = None,
        district: Optional[str] = None,
        area: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[str] = None,
        rental_type: Optional[str] = None,
        decoration: Optional[str] = None,
        orientation: Optional[str] = None,
        elevator: Optional[bool] = None,
        min_area: Optional[int] = None,
        max_area: Optional[int] = None,
        property_type: Optional[str] = None,
        subway_line: Optional[str] = None,
        max_subway_dist: Optional[int] = None,
        subway_station: Optional[str] = None,
        utilities_type: Optional[str] = None,
        available_from_before: Optional[str] = None,
        commute_to_xierqi_max: Optional[int] = None,
        sort_by: Optional[HouseSortBy] = None,
        sort_order: Optional[SortOrder] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> ApiResponse:
        """查询可租房源，支持按挂牌平台及多维度筛选。"""
        params: dict[str, Any] = {}
        if listing_platform is not None:
            params["listing_platform"] = listing_platform
        if district is not None:
            params["district"] = district
        if area is not None:
            params["area"] = area
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if bedrooms is not None:
            params["bedrooms"] = bedrooms
        if rental_type is not None:
            params["rental_type"] = rental_type
        if decoration is not None:
            params["decoration"] = decoration
        if orientation is not None:
            params["orientation"] = orientation
        if elevator is not None:
            params["elevator"] = "true" if elevator else "false"
        if min_area is not None:
            params["min_area"] = min_area
        if max_area is not None:
            params["max_area"] = max_area
        if property_type is not None:
            params["property_type"] = property_type
        if subway_line is not None:
            params["subway_line"] = subway_line
        if max_subway_dist is not None:
            params["max_subway_dist"] = max_subway_dist
        if subway_station is not None:
            params["subway_station"] = subway_station
        if utilities_type is not None:
            params["utilities_type"] = utilities_type
        if available_from_before is not None:
            params["available_from_before"] = available_from_before
        if commute_to_xierqi_max is not None:
            params["commute_to_xierqi_max"] = commute_to_xierqi_max
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = min(page_size or DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE)
        else:
            params["page_size"] = DEFAULT_PAGE_SIZE
        return self._request("GET", "/api/houses/by_platform", params=params, need_user_id=True)

    def get_houses_nearby(
        self,
        landmark_id: str,
        max_distance: Optional[float] = None,
        listing_platform: Optional[ListingPlatform] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> ApiResponse:
        """以地标为圆心查询在指定距离内的可租房源。"""
        params: dict[str, Any] = {"landmark_id": landmark_id}
        if max_distance is not None:
            params["max_distance"] = max_distance
        if listing_platform is not None:
            params["listing_platform"] = listing_platform
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = min(page_size, MAX_PAGE_SIZE)
        return self._request("GET", "/api/houses/nearby", params=params, need_user_id=True)

    def get_nearby_landmarks(
        self,
        community: str,
        landmark_type: Optional[NearbyLandmarkType] = None,
        max_distance_m: Optional[float] = None,
    ) -> ApiResponse:
        """查询某小区周边某类地标（商超/公园），按距离排序。"""
        params: dict[str, Any] = {"community": community}
        if landmark_type is not None:
            params["type"] = landmark_type
        if max_distance_m is not None:
            params["max_distance_m"] = max_distance_m
        return self._request("GET", "/api/houses/nearby_landmarks", params=params, need_user_id=True)

    def get_house_stats(self) -> ApiResponse:
        """获取房源统计信息（总套数、按状态/行政区/户型分布、价格区间等）。"""
        return self._request("GET", "/api/houses/stats", need_user_id=True)

    def rent_house(self, house_id: str, listing_platform: ListingPlatform) -> ApiResponse:
        """将当前用户视角下该房源设为已租。"""
        path = f"/api/houses/{house_id}/rent"
        return self._request(
            "POST",
            path,
            params={"listing_platform": listing_platform},
            need_user_id=True,
        )

    def terminate_rental(self, house_id: str, listing_platform: ListingPlatform) -> ApiResponse:
        """将当前用户视角下该房源恢复为可租。"""
        path = f"/api/houses/{house_id}/terminate"
        return self._request(
            "POST",
            path,
            params={"listing_platform": listing_platform},
            need_user_id=True,
        )

    def take_offline(self, house_id: str, listing_platform: ListingPlatform) -> ApiResponse:
        """将当前用户视角下该房源设为下架。"""
        path = f"/api/houses/{house_id}/offline"
        return self._request(
            "POST",
            path,
            params={"listing_platform": listing_platform},
            need_user_id=True,
        )


def create_client_and_init(
    base_url: str,
    user_id: str,
    session: Optional[requests.Session] = None,
    timeout: float = 30.0,
) -> FakeAppApiClient:
    """
    创建客户端并执行一次房源重置（建议每个新 session 调用）。
    """
    client = FakeAppApiClient(base_url=base_url, user_id=user_id, session=session, timeout=timeout)
    client.init_houses()
    return client
