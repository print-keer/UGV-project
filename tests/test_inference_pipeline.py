from __future__ import annotations

import unittest

from ai.inference.pipeline import run_mock_inference


class InferencePipelineTests(unittest.TestCase):
    def test_mock_inference_returns_expected_frames(self) -> None:
        results = run_mock_inference()

        self.assertEqual(len(results), 3)
        self.assertTrue(all(result.backend_name == "mock-yolov8n" for result in results))
        self.assertEqual(results[0].frame_id, "frame-clear-001")
        self.assertGreaterEqual(len(results[1].detections), 2)


if __name__ == "__main__":
    unittest.main()
