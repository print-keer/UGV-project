from __future__ import annotations

import unittest

from ai.training.train import DATASET_PRESETS


class TrainingPresetTests(unittest.TestCase):
    def test_mvrsd_presets_exist(self) -> None:
        self.assertIn("mvrsd-binary", DATASET_PRESETS)
        self.assertIn("mvrsd-multiclass", DATASET_PRESETS)
        self.assertEqual(
            DATASET_PRESETS["mvrsd-multiclass"].data_config,
            "ai/dataset/mvrsd_multiclass.yaml",
        )


if __name__ == "__main__":
    unittest.main()
