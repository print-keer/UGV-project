from __future__ import annotations

import unittest

from ai.inference.pipeline import run_mock_inference
from ai.threat_classifier.classifier import assess_detections, classify_label
from ai.training.config import TrainingConfig


class ThreatClassifierTests(unittest.TestCase):
    def test_harmful_detection_triggers_alert(self) -> None:
        threat_frame = run_mock_inference()[1]
        assessment = assess_detections(threat_frame.detections)

        self.assertTrue(assessment.alert_required)
        self.assertEqual(assessment.highest_priority_label, "harmful")
        self.assertIn("[ALERT]", assessment.summary)

    def test_unknown_detection_stays_non_alerting(self) -> None:
        unknown_frame = run_mock_inference()[2]
        assessment = assess_detections(unknown_frame.detections)

        self.assertFalse(assessment.alert_required)
        self.assertEqual(assessment.unknown_count, 1)
        self.assertEqual(classify_label("unknown_object"), "unknown")

    def test_training_command_matches_yolo_layout(self) -> None:
        config = TrainingConfig()

        self.assertIn("model=yolov8n.pt", config.build_command())
        self.assertIn("data=ai/dataset/data.yaml", config.build_command())


if __name__ == "__main__":
    unittest.main()
