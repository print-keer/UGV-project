from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mission_controller.demo import run_demo, run_dynamic_demo, run_topic_demo


class DemoPipelineTests(unittest.TestCase):
    def test_demo_pipeline_returns_reports_for_sample_maps(self) -> None:
        reports = run_demo()

        self.assertGreaterEqual(len(reports), 2)
        self.assertTrue(all("map_name" in report for report in reports))
        self.assertTrue(all("path_found" in report for report in reports))
        self.assertTrue(all(report["path_found"] for report in reports))
        self.assertTrue(all(report["planner_state"] == "success" for report in reports))
        self.assertTrue(all(report["navigation_state"] == "reached_goal" for report in reports))
        self.assertTrue(all(report["reached_goal"] for report in reports))
        self.assertTrue(all(report["progress_steps"] >= 1 for report in reports))
        self.assertTrue(all(report["motor_status_count"] >= 1 for report in reports))
        self.assertTrue(all("applied" in report["motor_states"] for report in reports))

    def test_topic_demo_exercises_replanning_flow(self) -> None:
        reports = run_topic_demo()

        self.assertGreaterEqual(len(reports), 2)
        self.assertTrue(all(report["replanned"] for report in reports))
        self.assertTrue(all(report["final_revision"] == 1 for report in reports))
        self.assertTrue(all(not report["final_reached_goal"] for report in reports))
        self.assertTrue(all(report["final_motor_status_count"] >= 1 for report in reports))
        self.assertTrue(
            all("/navigation/replan_request" in report["published_topics"] for report in reports)
        )

    def test_dynamic_demo_reports_replanning_timeline(self) -> None:
        reports = run_dynamic_demo()

        self.assertGreaterEqual(len(reports), 1)
        self.assertTrue(all(report["total_replans"] >= 1 for report in reports))
        self.assertTrue(all(len(report["revisions"]) >= 2 for report in reports))
        self.assertTrue(all(len(report["progress_steps"]) == len(report["revisions"]) for report in reports))



if __name__ == "__main__":
    unittest.main()
