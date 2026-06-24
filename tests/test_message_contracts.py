from __future__ import annotations

import unittest

from ai.inference.pipeline import run_mock_inference
from ai.threat_classifier.contracts import (
    build_assessment_payload,
    deserialize_assessment,
    deserialize_detection_result,
    serialize_detection_result,
)


class MessageContractTests(unittest.TestCase):
    def test_detection_payload_round_trip_preserves_fields(self) -> None:
        result = run_mock_inference()[1]
        payload = serialize_detection_result(result)
        restored = deserialize_detection_result(payload)

        self.assertEqual(restored.frame_id, result.frame_id)
        self.assertEqual(restored.backend_name, result.backend_name)
        self.assertEqual(len(restored.detections), len(result.detections))
        self.assertEqual(restored.detections[0].label, result.detections[0].label)

    def test_assessment_payload_contains_alert_fields(self) -> None:
        result = run_mock_inference()[1]
        payload = build_assessment_payload(result)
        data = deserialize_assessment(payload)

        self.assertEqual(data["frame_id"], result.frame_id)
        self.assertTrue(data["alert_required"])
        self.assertIn("summary", data)


if __name__ == "__main__":
    unittest.main()
