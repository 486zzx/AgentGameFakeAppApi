#!/usr/bin/env python3
"""
租房仿真 API 客户端使用示例，可直接运行。

用法：
  # 指定服务地址和工号（必填）
  python run_example.py --base-url http://IP:8080 --user-id 你的工号

  # 可选：只做地标查询演示（不调房源接口，可不传 user-id）
  python run_example.py --base-url http://IP:8080 --landmarks-only
"""
import argparse
import json
import sys

# 支持直接运行：先加入项目根目录
sys.path.insert(0, ".")

from agent_game_fake_app_api import FakeAppApiClient, create_client_and_init


def main() -> None:
    parser = argparse.ArgumentParser(
        description="租房仿真 API 客户端示例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="API 基地址，例如 http://192.168.1.100:8080",
    )
    parser.add_argument(
        "--user-id",
        default="",
        help="用户工号（房源相关接口必填；仅地标演示可不填）",
    )
    parser.add_argument(
        "--landmarks-only",
        action="store_true",
        help="仅演示地标接口（不需 X-User-ID）",
    )
    parser.add_argument(
        "--no-init",
        action="store_true",
        help="不调用房源数据重置接口（默认会先调用 init）",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    user_id = (args.user_id or "demo_user").strip()

    print("=" * 60)
    print("租房仿真 API 客户端示例")
    print("=" * 60)
    print(f"  base_url: {base_url}")
    print(f"  user_id:  {user_id}")
    print(f"  landmarks_only: {args.landmarks_only}, no_init: {args.no_init}")
    print()

    try:
        if args.landmarks_only:
            client = FakeAppApiClient(base_url=base_url, user_id=user_id)
            print("[1] 地标统计 get_landmark_stats()")
            r = client.get_landmark_stats()
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print()
            print("[2] 地标列表 get_landmarks(category='subway', district='海淀')")
            r = client.get_landmarks(category="subway", district="海淀")
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print()
            print("[3] 按名称查地标 get_landmark_by_name('西二旗站')")
            r = client.get_landmark_by_name("西二旗站")
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            if not args.no_init:
                print("[0] 创建客户端并执行房源数据重置 create_client_and_init()")
                client = create_client_and_init(base_url=base_url, user_id=user_id)
                print("    init 调用成功")
            else:
                client = FakeAppApiClient(base_url=base_url, user_id=user_id)
                print("[0] 仅创建客户端（未调用 init）")

            print()
            print("[1] 地标统计 get_landmark_stats()")
            r = client.get_landmark_stats()
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print()
            print("[2] 房源统计 get_house_stats()")
            r = client.get_house_stats()
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print()
            print("[3] 按平台查房源 get_houses_by_platform(district='海淀', page_size=3)")
            r = client.get_houses_by_platform(district="海淀", page_size=3)
            print(json.dumps(r, ensure_ascii=False, indent=2))

        print()
        print("=" * 60)
        print("示例运行完成")
        print("=" * 60)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
