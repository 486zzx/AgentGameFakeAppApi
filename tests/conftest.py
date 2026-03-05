"""Pytest 公共 fixture：Mock Session、客户端实例、通用响应。"""
import json
from unittest.mock import MagicMock

import pytest

from agent_game_fake_app_api import FakeAppApiClient

BASE_URL = "http://test.example.com:8080"
USER_ID = "test_user_001"


def make_response(body: dict, status_code: int = 200):
    """构造带 raise_for_status 和 json 的响应对象。"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = json.dumps(body, ensure_ascii=False)
    resp.json.return_value = body

    def raise_for_status():
        if status_code >= 400:
            raise Exception(f"HTTP {status_code}")

    resp.raise_for_status = raise_for_status
    return resp


@pytest.fixture
def mock_session():
    """可配置的 Mock Session，默认返回 200 + 空 data。"""
    session = MagicMock()
    session.request.return_value = make_response({"code": 0, "data": {}})
    return session


@pytest.fixture
def client(mock_session):
    """使用 Mock Session 的客户端，便于断言请求参数。"""
    return FakeAppApiClient(
        base_url=BASE_URL,
        user_id=USER_ID,
        session=mock_session,
    )


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def user_id():
    return USER_ID
