#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""每种无线驱动、每套 H5000M 方案保留最近 3 个完整固件 Release。"""

import argparse
from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote


KEEP_COUNT = 3
SOURCE_DRIVERS = {
    "immortalwrt-master": "mt76",
    "VIKINGYFY-owrt": "mt76",
    "chasey-dev-25.12": "mt76",
    "chasey-dev-25.12-dev-wifi7": "mt_wifi7",
}


def load_configs(directory):
    configs = sorted(
        path.stem for path in directory.glob("H5000M-*.txt")
        if re.search(
            r"^CONFIG_TARGET_DEVICE_mediatek_filogic_DEVICE_hiveton_h5000m=y$",
            path.read_text(), re.M,
        )
    )
    if not configs:
        raise ValueError(f"{directory} 中没有 H5000M 设备配置，拒绝清理")
    return configs


def classify(release, configs):
    """未知标签、草稿及尚未上传完整镜像的 Release 均不进入清理计划。"""
    if release.get("draft"):
        return None
    tag = release.get("tag_name", "")
    for config in sorted(configs, key=len, reverse=True):
        match = re.fullmatch(
            re.escape(config) + r"-(.+)-(\d{2}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})",
            tag,
        )
        if not match:
            continue
        driver = SOURCE_DRIVERS.get(match[1])
        if driver is None:
            continue
        try:
            datetime.strptime(match[2], "%y.%m.%d-%H.%M.%S")
        except ValueError:
            return None
        pattern = re.escape(config) + r"-\d{8}-sysupgrade\.bin"
        if not any(
            asset.get("state") == "uploaded"
            and isinstance(asset.get("size"), int) and asset["size"] > 0
            and re.fullmatch(pattern, asset.get("name", ""))
            for asset in release.get("assets", [])
        ):
            return None
        return driver, config
    return None


def publication_key(release):
    try:
        published = datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError("发布时间缺少时区")
        release_id = release["id"]
        if type(release_id) is not int or release_id <= 0:
            raise ValueError("Release ID 非法")
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"{release.get('tag_name')}: Release 元数据无效，拒绝清理") from error
    return published, release_id


def plan_releases(releases, configs, only_config=None):
    if not configs or (only_config and only_config not in configs):
        raise ValueError("H5000M 配置范围无效，拒绝清理")
    groups = defaultdict(list)
    ignored = []
    seen = set()
    for release in releases:
        key = classify(release, configs)
        if key is None or (only_config and key[1] != only_config):
            ignored.append(release)
            continue
        publication_key(release)
        if release["id"] not in seen:
            seen.add(release["id"])
            groups[key].append(release)
    keep, delete = [], []
    for key in sorted(groups):
        ordered = sorted(groups[key], key=publication_key, reverse=True)
        keep.extend((key, release) for release in ordered[:KEEP_COUNT])
        delete.extend((key, release) for release in ordered[KEEP_COUNT:])
    return keep, delete, ignored


def gh_api(endpoint, method="GET"):
    args = ["gh", "api", endpoint]
    if method != "GET":
        args.extend(["--method", method, "--silent"])
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    return json.loads(result.stdout) if method == "GET" else None


def fetch_releases(repo, api=gh_api):
    """先收集全部分页；稍后全局排序，不能依赖 API 的页内/页间顺序。"""
    releases = []
    page = 1
    while True:
        batch = api(f"repos/{repo}/releases?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("GitHub Releases API 返回格式不正确，拒绝清理")
        if not batch:
            return releases
        releases.extend(batch)
        page += 1


def apply_deletions(repo, deletions, api=gh_api):
    for key, release in deletions:
        # Release 删除失败时必须停止，不能继续删除它的 tag。
        api(f"repos/{repo}/releases/{release['id']}", method="DELETE")
        api(f"repos/{repo}/git/refs/tags/{quote(release['tag_name'], safe='')}", method="DELETE")
        print(f"[deleted] {key[0]} / {key[1]}: {release['tag_name']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--config", help="发布后仅轮换当前方案，避免影响其他构建任务")
    parser.add_argument("--config-dir", type=Path, default=Path(__file__).resolve().parents[2] / "Config")
    parser.add_argument("--apply", action="store_true", help="实际删除；默认只预览")
    args = parser.parse_args()
    if not args.repo or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo 必须是 owner/repo")
    configs = load_configs(args.config_dir)
    releases = fetch_releases(args.repo)
    keep, delete, ignored = plan_releases(releases, configs, args.config)
    print(f"{'APPLY' if args.apply else 'PREVIEW'}: {args.repo}; 每种驱动 × 每套方案保留 {KEEP_COUNT} 版")
    for action, items in (("keep", keep), ("delete" if args.apply else "would-delete", delete)):
        for key, release in items:
            print(f"[{action}] {key[0]} / {key[1]}: {release['tag_name']}")
    print(f"保留 {len(keep)}，{'删除' if args.apply else '计划删除'} {len(delete)}，范围外/未完成 {len(ignored)}")
    if args.apply:
        apply_deletions(args.repo, delete)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as output:
            output.write(
                f"### 固件保留策略：{'实际执行' if args.apply else '仅预览'}\n\n"
                f"每种驱动 × 每套方案保留最近 {KEEP_COUNT} 版。\n\n"
                f"保留 {len(keep)}，{'已删除' if args.apply else '计划删除'} {len(delete)}，"
                f"范围外/未完成 {len(ignored)}。\n"
            )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"::error::Release 清理失败：{error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        sys.exit(1)
