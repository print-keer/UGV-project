from __future__ import annotations

import unittest
from pathlib import Path

from ai.inference.backends import RuntimeFrame, YoloVisionBackend
from ai.inference.pipeline import run_runtime_inference
from ai.training.config import TrainingConfig


class RuntimeInferenceTests(unittest.TestCase):
    def test_runtime_inference_raises_when_model_is_missing(self) -> None:
        frame = RuntimeFrame(frame_id="test", image=object(), description="test frame")

        with self.assertRaises(FileNotFoundError):
            run_runtime_inference([frame], model_path="ai/models/missing.pt")

    def test_yolo_backend_is_not_ready_without_weights(self) -> None:
        backend = YoloVisionBackend("ai/models/missing.pt")
        self.assertFalse(backend.is_ready())

    def test_training_config_resolves_output_model_path(self) -> None:
        config = TrainingConfig()
        resolved = config.resolved_output_model_path(Path("/tmp/repo"))
        self.assertEqual(resolved, Path("/tmp/repo/ai/models/best.pt"))


if __name__ == "__main__":
    unittest.main()
