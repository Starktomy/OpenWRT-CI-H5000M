# SPDX-License-Identifier: MIT
"""验证固件轮换的分组、全局排序、上传状态和删除失败行为。"""

import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("retention", ROOT / ".github/scripts/release-retention.py")
retention = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retention)
CONFIGS = ["H5000M-" + variant for variant in ("qmodem-next", "qmodem", "modem-pro", "mt5700", "mt5700m")]


def release(release_id, config, source="immortalwrt-master", day=1, **extra):
    return {
        "id": release_id,
        "tag_name": f"{config}-{source}-26.11.{day:02d}-08.00.00",
        "published_at": f"2026-11-{day:02d}T00:00:00Z",
        "draft": False,
        "assets": [{"name": f"{config}-202611{day:02d}-sysupgrade.bin", "size": 80000000, "state": "uploaded"}],
        **extra,
    }


class RetentionTests(unittest.TestCase):
    def test_all_ten_groups_keep_three(self):
        builds = []
        for config in CONFIGS:
            for source in ("immortalwrt-master", "chasey-dev-25.12-dev-wifi7"):
                for day in range(1, 6):
                    builds.append(release(len(builds) + 1, config, source, day))
        keep, delete, ignored = retention.plan_releases(builds, CONFIGS)
        self.assertEqual(len(keep), 30)
        self.assertEqual(len(delete), 20)
        self.assertEqual(ignored, [])
        for driver in ("mt76", "mt_wifi7"):
            for config in CONFIGS:
                retained = [r for group, r in keep if group == (driver, config)]
                self.assertEqual([r["published_at"][8:10] for r in retained], ["05", "04", "03"])

    def test_same_driver_sources_share_three_slots(self):
        builds = [release(i, CONFIGS[0], source, i) for i, source in enumerate(
            ("immortalwrt-master", "VIKINGYFY-owrt", "chasey-dev-25.12", "VIKINGYFY-owrt"), 1
        )]
        keep, delete, _ = retention.plan_releases(builds, CONFIGS)
        self.assertEqual([r["id"] for _, r in keep], [4, 3, 2])
        self.assertEqual([r["id"] for _, r in delete], [1])

    def test_qmodem_prefix_does_not_mix_next(self):
        builds = [release(i, CONFIGS[0], day=i) for i in range(1, 5)]
        builds += [release(10, "H5000M-qmodem", day=1)]
        keep, delete, _ = retention.plan_releases(builds, CONFIGS)
        self.assertIn(10, [r["id"] for _, r in keep])
        self.assertEqual([r["id"] for _, r in delete], [1])

    def test_pagination_sorted_globally_and_duplicates_ignored(self):
        builds = [release(i, CONFIGS[0], day=i) for i in range(1, 5)]
        pages = {1: [builds[0], builds[3]], 2: [builds[2], builds[1], builds[3]], 3: []}
        calls = []

        def api(endpoint):
            calls.append(endpoint)
            return pages[int(endpoint.rsplit("=", 1)[1])]

        fetched = retention.fetch_releases("owner/repo", api)
        keep, delete, _ = retention.plan_releases(fetched, CONFIGS)
        self.assertEqual(len(calls), 3)
        self.assertEqual([r["id"] for _, r in keep], [4, 3, 2])
        self.assertEqual([r["id"] for _, r in delete], [1])

    def test_drafts_incomplete_and_unknown_tags_do_not_evict_good_builds(self):
        builds = [release(i, CONFIGS[0], day=i) for i in range(1, 4)]
        skipped = [
            release(4, CONFIGS[0], day=4, draft=True),
            release(5, CONFIGS[0], day=5, assets=[]),
            release(6, CONFIGS[0], day=6, assets=[{"name": f"{CONFIGS[0]}-20261106-sysupgrade.bin", "size": 80000000, "state": "starter"}]),
            release(7, CONFIGS[0], day=7, tag_name="stable-mt76-qmodem-next-v1"),
            release(8, CONFIGS[0], day=8, tag_name="unrecognized-build"),
            release(9, CONFIGS[0], source="unrecognized-source", day=9),
            release(10, CONFIGS[0], day=10, assets=[{"name": "wrong-variant-sysupgrade.bin", "size": 80000000, "state": "uploaded"}]),
            release(11, CONFIGS[0], day=11, assets=[{"name": f"{CONFIGS[0]}-20261111-sysupgrade.bin", "size": 0, "state": "uploaded"}]),
        ]
        keep, delete, ignored = retention.plan_releases(builds + skipped, CONFIGS)
        self.assertEqual(len(keep), 3)
        self.assertEqual(delete, [])
        self.assertEqual(ignored, skipped)

    def test_publish_fourth_evicts_only_oldest_in_current_profile(self):
        builds = [release(i, CONFIGS[0], day=i) for i in range(1, 5)]
        builds += [release(100 + i, CONFIGS[1], day=i) for i in range(1, 5)]
        keep, delete, ignored = retention.plan_releases(builds, CONFIGS, CONFIGS[0])
        self.assertEqual([r["id"] for _, r in keep], [4, 3, 2])
        self.assertEqual([r["id"] for _, r in delete], [1])
        self.assertEqual(len(ignored), 4)

    def test_invalid_metadata_aborts_before_any_delete(self):
        builds = [release(i, CONFIGS[0], day=i) for i in range(1, 5)]
        builds[-1]["published_at"] = "invalid-date"
        with self.assertRaisesRegex(ValueError, "元数据无效"):
            retention.plan_releases(builds, CONFIGS)
        with self.assertRaises(ValueError):
            retention.plan_releases([], [])
        with self.assertRaises(ValueError):
            retention.plan_releases([], CONFIGS, "H5000M-unknown")

    def test_release_delete_failure_never_deletes_tag(self):
        calls = []

        def api(endpoint, method):
            calls.append((endpoint, method))
            raise subprocess.CalledProcessError(1, ["gh", "api", endpoint])

        with self.assertRaises(subprocess.CalledProcessError):
            retention.apply_deletions("owner/repo", [(("mt76", CONFIGS[0]), release(1, CONFIGS[0]))], api)
        self.assertEqual(calls, [("repos/owner/repo/releases/1", "DELETE")])

    def test_success_removes_release_then_its_tag(self):
        calls = []

        def api(endpoint, method):
            calls.append((endpoint, method))

        build = release(1, CONFIGS[0])
        retention.apply_deletions("owner/repo", [(("mt76", CONFIGS[0]), build)], api)
        self.assertEqual(calls, [
            ("repos/owner/repo/releases/1", "DELETE"),
            (f"repos/owner/repo/git/refs/tags/{build['tag_name']}", "DELETE"),
        ])

    def test_configs_are_real_board_profiles(self):
        self.assertEqual(set(retention.load_configs(ROOT / "Config")), set(CONFIGS))


if __name__ == "__main__":
    unittest.main()
