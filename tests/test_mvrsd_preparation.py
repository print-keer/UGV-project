from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai.dataset.prepare_mvrsd import prepare_mvrsd_dataset


class MvrsdPreparationTests(unittest.TestCase):
    def test_prepare_mvrsd_dataset_collapses_all_classes_to_harmful(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_root = root / "source"
            (source_root / "images" / "train").mkdir(parents=True)
            (source_root / "images" / "val").mkdir(parents=True)
            (source_root / "labels" / "train").mkdir(parents=True)
            (source_root / "labels" / "val").mkdir(parents=True)
            (source_root / "labels" / "classes.txt").write_text(
                "SMV\nLMV\nAFV\nCV\nMCV\n",
                encoding="utf-8",
            )
            (source_root / "images" / "train" / "a.jpg").write_bytes(b"train")
            (source_root / "images" / "val" / "b.jpg").write_bytes(b"val")
            (source_root / "labels" / "train" / "a.txt").write_text(
                "4 0.5 0.5 0.1 0.1\n1 0.3 0.3 0.2 0.2\n",
                encoding="utf-8",
            )
            (source_root / "labels" / "val" / "b.txt").write_text(
                "2 0.1 0.2 0.3 0.4\n",
                encoding="utf-8",
            )

            output_root = root / "binary"
            summary = prepare_mvrsd_dataset(source_root, output_root)

            self.assertEqual(summary["source_classes"], 5)
            self.assertEqual(summary["train_images"], 1)
            self.assertEqual(summary["val_images"], 1)
            self.assertIn("0 0.5 0.5 0.1 0.1", (output_root / "labels" / "train" / "a.txt").read_text())
            self.assertEqual(
                (output_root / "data.yaml").read_text(encoding="utf-8").splitlines()[-1],
                "  0: harmful",
            )


if __name__ == "__main__":
    unittest.main()
