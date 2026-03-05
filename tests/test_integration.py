"""
集成测试：对真实服务发起请求。默认跳过，需设置环境变量后运行。

运行方式：
  RUN_INTEGRATION=1 BASE_URL=http://IP:8080 USER_ID=你的工号 pytest tests/test_integration.py -v
  # 或
  set RUN_INTEGRATION=1 && set BASE_URL=http://192.168.1.100:8080 && set USER_ID=12345 && pytest tests/test_integration.py -v
"""
import os

import pytest

from agent_game_fake_app_api import FakeAppApiClient, create_client_and_init

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
USER_ID = os.environ.get("USER_ID", "")
RUN_INTEGRATION = os.environ.get("RUN_INTEGRATION", "").strip() in ("1", "true", "True", "yes")


def _skip_if_no_env():
    if not RUN_INTEGRATION or not BASE_URL:
        pytest.skip("集成测试已跳过：设置 RUN_INTEGRATION=1 和 BASE_URL 后运行")
    if not USER_ID:
        pytest.skip("集成测试需要设置 USER_ID（房源接口与 init 必填）")


@pytest.fixture(scope="module")
def integration_client():
    _skip_if_no_env()
    return create_client_and_init(base_url=BASE_URL, user_id=USER_ID)


def test_integration_landmark_stats(integration_client):
    r = integration_client.get_landmark_stats()
    assert r is not None
    assert "data" in r or "code" in r


def test_integration_landmarks_list(integration_client):
    r = integration_client.get_landmarks(category="subway", district="海淀")
    assert r is not None


def test_integration_house_stats(integration_client):
    r = integration_client.get_house_stats()
    assert r is not None


def test_integration_houses_by_platform(integration_client):
    r = integration_client.get_houses_by_platform(district="海淀", page_size=2)
    assert r is not None
    data = r.get("data") or r
    if isinstance(data, dict) and "items" in data:
        assert len(data["items"]) <= 2


def test_integration_landmark_by_name(integration_client):
    r = integration_client.get_landmark_by_name("西二旗站")
    assert r is not None
