"""
客户端单元测试：覆盖全部 16 个接口的请求方法、路径、参数与 X-User-ID。
不依赖真实服务，使用 Mock Session 可直接运行。
"""
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError
from urllib.parse import parse_qs, urlparse

from agent_game_fake_app_api import FakeAppApiClient, create_client_and_init


def _request_call(client, mock_session):
    """取最后一次 request 调用的 (method, url, headers)。"""
    assert mock_session.request.called
    call = mock_session.request.call_args
    # Session.request(method, url, **kwargs) -> args=(method, url), kwargs={headers, timeout, ...}
    method, url = call[0][0], call[0][1]
    headers = call[1].get("headers", {})
    return method, url, headers


def _query(url):
    """解析 URL 的 query 部分为 dict。"""
    q = urlparse(url).query
    return parse_qs(q) if q else {}


# ---------- 房源数据重置（需求：POST /api/houses/init，必带 X-User-ID） ----------
def test_init_houses(client, mock_session, base_url, user_id):
    client.init_houses()
    method, url, headers = _request_call(client, mock_session)
    assert method == "POST"
    assert url.startswith(base_url)
    assert "/api/houses/init" in url
    assert headers.get("X-User-ID") == user_id


# ---------- 地标接口（需求：不需 X-User-ID） ----------
def test_get_landmarks(client, mock_session, base_url):
    client.get_landmarks(category="subway", district="海淀")
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/landmarks" in url
    assert urlparse(url).path.endswith("/api/landmarks")
    q = _query(url)
    assert q.get("category") == ["subway"]
    assert q.get("district") == ["海淀"]
    assert "X-User-ID" not in headers or headers.get("X-User-ID") is None


def test_get_landmarks_no_params(client, mock_session):
    client.get_landmarks()
    _, url, _ = _request_call(client, mock_session)
    assert "/api/landmarks" in url
    assert "?" not in url or _query(url) == {}


def test_get_landmark_by_name(client, mock_session, base_url):
    client.get_landmark_by_name("西二旗站")
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/landmarks/name/" in url
    assert "西二旗站" in url
    assert headers.get("X-User-ID") is None or "X-User-ID" not in headers


def test_search_landmarks(client, mock_session):
    client.search_landmarks("国贸", category="landmark", district="朝阳")
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("q") == ["国贸"]
    assert q.get("category") == ["landmark"]
    assert q.get("district") == ["朝阳"]


def test_get_landmark_by_id(client, mock_session):
    client.get_landmark_by_id("SS_001")
    _, url, _ = _request_call(client, mock_session)
    assert "/api/landmarks/SS_001" in url


def test_get_landmark_stats(client, mock_session, base_url):
    client.get_landmark_stats()
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/landmarks/stats" in url
    assert "X-User-ID" not in headers or headers.get("X-User-ID") is None


# ---------- 房源接口（需求：必带 X-User-ID） ----------
def test_get_house(client, mock_session, user_id):
    client.get_house("HF_2001")
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/houses/HF_2001" in url
    assert headers.get("X-User-ID") == user_id


def test_get_house_listings(client, mock_session, user_id):
    client.get_house_listings("HF_2001")
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/houses/listings/HF_2001" in url
    assert headers.get("X-User-ID") == user_id


def test_get_houses_by_community(client, mock_session, user_id):
    client.get_houses_by_community(community="建清园(南区)", page=1, page_size=20)
    _, url, headers = _request_call(client, mock_session)
    assert "/api/houses/by_community" in url
    q = _query(url)
    assert q.get("community") == ["建清园(南区)"]
    assert q.get("page") == ["1"]
    assert q.get("page_size") == ["20"]
    assert headers.get("X-User-ID") == user_id


def test_get_houses_by_community_listing_platform(client, mock_session):
    client.get_houses_by_community(community="保利锦上(二期)", listing_platform="链家")
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("listing_platform") == ["链家"]


def test_get_houses_by_platform(client, mock_session, user_id):
    client.get_houses_by_platform(
        district="海淀",
        min_price=2000,
        max_price=5000,
        max_subway_dist=800,
        page=1,
        page_size=10,
    )
    _, url, headers = _request_call(client, mock_session)
    assert "/api/houses/by_platform" in url
    q = _query(url)
    assert q.get("district") == ["海淀"]
    assert q.get("min_price") == ["2000"]
    assert q.get("max_price") == ["5000"]
    assert q.get("max_subway_dist") == ["800"]
    assert q.get("page_size") == ["10"]
    assert headers.get("X-User-ID") == user_id


def test_get_houses_by_platform_default_page_size(client, mock_session):
    """未传 page_size 时使用默认 10。"""
    client.get_houses_by_platform(district="朝阳")
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("page_size") == ["10"]


def test_get_houses_by_platform_page_size_capped(client, mock_session):
    """page_size 超过 10000 时被限制为 10000。"""
    client.get_houses_by_platform(district="海淀", page_size=20000)
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("page_size") == ["10000"]


def test_get_houses_by_platform_rental_type_decoration(client, mock_session):
    client.get_houses_by_platform(
        rental_type="整租",
        decoration="精装",
        sort_by="price",
        sort_order="asc",
    )
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("rental_type") == ["整租"]
    assert q.get("decoration") == ["精装"]
    assert q.get("sort_by") == ["price"]
    assert q.get("sort_order") == ["asc"]


def test_get_houses_by_platform_elevator(client, mock_session):
    client.get_houses_by_platform(elevator=True)
    _, url, _ = _request_call(client, mock_session)
    q = _query(url)
    assert q.get("elevator") == ["true"]
    client.get_houses_by_platform(elevator=False)
    _, url2, _ = _request_call(client, mock_session)
    q2 = _query(url2)
    assert q2.get("elevator") == ["false"]


def test_get_houses_nearby(client, mock_session, user_id):
    client.get_houses_nearby(landmark_id="SS_001", max_distance=2000, page_size=5)
    _, url, headers = _request_call(client, mock_session)
    assert "/api/houses/nearby" in url
    q = _query(url)
    assert q.get("landmark_id") == ["SS_001"]
    assert q.get("max_distance") == ["2000"]
    assert q.get("page_size") == ["5"]
    assert headers.get("X-User-ID") == user_id


def test_get_nearby_landmarks(client, mock_session, user_id):
    client.get_nearby_landmarks(
        community="建清园(南区)",
        landmark_type="shopping",
        max_distance_m=3000,
    )
    _, url, headers = _request_call(client, mock_session)
    assert "/api/houses/nearby_landmarks" in url
    q = _query(url)
    assert q.get("community") == ["建清园(南区)"]
    assert q.get("type") == ["shopping"]
    assert q.get("max_distance_m") == ["3000"]
    assert headers.get("X-User-ID") == user_id


def test_get_house_stats(client, mock_session, user_id):
    client.get_house_stats()
    method, url, headers = _request_call(client, mock_session)
    assert method == "GET"
    assert "/api/houses/stats" in url
    assert headers.get("X-User-ID") == user_id


# ---------- 租房/退租/下架（需求：必须调 API，listing_platform 必填） ----------
def test_rent_house(client, mock_session, user_id):
    client.rent_house("HF_2001", "安居客")
    method, url, headers = _request_call(client, mock_session)
    assert method == "POST"
    assert "/api/houses/HF_2001/rent" in url
    q = _query(url)
    assert q.get("listing_platform") == ["安居客"]
    assert headers.get("X-User-ID") == user_id


def test_terminate_rental(client, mock_session, user_id):
    client.terminate_rental("HF_2001", "链家")
    method, url, headers = _request_call(client, mock_session)
    assert method == "POST"
    assert "/api/houses/HF_2001/terminate" in url
    assert _query(url).get("listing_platform") == ["链家"]
    assert headers.get("X-User-ID") == user_id


def test_take_offline(client, mock_session, user_id):
    client.take_offline("HF_2001", "58同城")
    method, url, headers = _request_call(client, mock_session)
    assert method == "POST"
    assert "/api/houses/HF_2001/offline" in url
    assert _query(url).get("listing_platform") == ["58同城"]
    assert headers.get("X-User-ID") == user_id


# ---------- create_client_and_init 会调用 init ----------
def test_create_client_and_init_calls_init(mock_session, base_url, user_id):
    mock_session.request.return_value.json.return_value = {"code": 0, "data": None}
    client = create_client_and_init(base_url=base_url, user_id=user_id, session=mock_session)
    assert mock_session.request.call_count >= 1
    first_call_url = mock_session.request.call_args_list[0][0][1]  # (method, url)
    assert "/api/houses/init" in first_call_url
    assert client.user_id == user_id


# ---------- 响应解析与错误处理 ----------
def test_returns_json_body(client, mock_session):
    mock_session.request.return_value.json.return_value = {
        "code": 0,
        "data": {"total": 42, "items": []},
    }
    r = client.get_house_stats()
    assert r.get("data", {}).get("total") == 42


def test_raises_on_http_error(mock_session, base_url, user_id):
    resp = MagicMock()
    resp.status_code = 400
    resp.raise_for_status.side_effect = HTTPError("400")
    resp.json.return_value = {"message": "X-User-ID required"}
    mock_session.request.return_value = resp

    client = FakeAppApiClient(base_url=base_url, user_id=user_id, session=mock_session)
    with pytest.raises(HTTPError):
        client.get_house("HF_2001")


# ---------- base_url 规范化 ----------
def test_base_url_trailing_slash(mock_session):
    """base_url 末尾斜杠会被去掉，请求路径正确。"""
    c = FakeAppApiClient(base_url="http://host:8080/", user_id="u", session=mock_session)
    c.get_landmark_stats()
    url = mock_session.request.call_args[0][1]  # (method, url)
    assert url == "http://host:8080/api/landmarks/stats"
