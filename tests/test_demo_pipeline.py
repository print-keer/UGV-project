from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mission_controller.demo import run_demo


class DemoPipelineTests(unittest.TestCase):
    def test_demo_pipeline_returns_reports_for_sample_maps(self) -> None:
        reports = run_demo()

        self.assertGreaterEqual(len(reports), 2)
        self.assertTrue(all("map_name" in report for report in reports))
        self.assertTrue(all("path_found" in report for report in reports))
        self.assertTrue(all(report["path_found"] for report in reports))


if __name__ == "__main__":
    unittest.main()
