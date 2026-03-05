#!/usr/bin/env python3
"""
集成测试执行脚本：对真实租房仿真 API 发起请求并校验。

用法：
  # 命令行传参（推荐）
  python run_integration_tests.py --base-url http://IP:8080 --user-id 你的工号

  # 环境变量
  set BASE_URL=http://IP:8080
  set USER_ID=你的工号
  python run_integration_tests.py

  # 仅指定 base-url，user-id 从环境变量读取
  python run_integration_tests.py --base-url http://192.168.1.100:8080
"""
import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="运行集成测试（需真实租房仿真 API 服务）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BASE_URL", ""),
        help="API 基地址，如 http://192.168.1.100:8080（也可用环境变量 BASE_URL）",
    )
    parser.add_argument(
        "--user-id",
        default=os.environ.get("USER_ID", ""),
        help="用户工号（也可用环境变量 USER_ID）",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=True,
        help="详细输出（默认开启）",
    )
    args = parser.parse_args()

    base_url = (args.base_url or "").strip().rstrip("/")
    user_id = (args.user_id or "").strip()

    if not base_url:
        print("错误：未设置 base-url。请使用 --base-url 或环境变量 BASE_URL。", file=sys.stderr)
        return 1
    if not user_id:
        print("错误：未设置 user-id。请使用 --user-id 或环境变量 USER_ID。", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["RUN_INTEGRATION"] = "1"
    env["BASE_URL"] = base_url
    env["USER_ID"] = user_id

    cmd = [sys.executable, "-m", "pytest", "tests/test_integration.py", "-v", "--tb=short"]
    print(f"集成测试：BASE_URL={base_url}, USER_ID={user_id}")
    print("执行:", " ".join(cmd))
    print()
    ret = subprocess.run(cmd, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
    return ret.returncode


if __name__ == "__main__":
    sys.exit(main())
