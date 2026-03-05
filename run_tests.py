#!/usr/bin/env python3
"""
一键运行全部单元测试（不依赖真实服务，可直接跑）。

用法：
  python run_tests.py
  python run_tests.py -v
  python run_tests.py --no-cov
"""
import sys

import pytest

if __name__ == "__main__":
    # 默认只跑非集成测试；可加 -m "not integration" 若以后给集成测试打 mark
    args = ["-v", "--tb=short", "tests/"]
    if "--no-cov" in sys.argv:
        sys.argv.remove("--no-cov")
    else:
        try:
            import pytest_cov  # noqa: F401
            args.extend(["--cov=agent_game_fake_app_api", "--cov-report=term-missing"])
        except ImportError:
            pass
    sys.exit(pytest.main(args))
