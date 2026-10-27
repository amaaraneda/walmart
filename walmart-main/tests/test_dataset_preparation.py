import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from backend.prepare_shelf_dataset import prepare


class DatasetPreparationTests(unittest.TestCase):
    def test_scene_split_and_unknown_image_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            for scene in range(12):
                for variant in range(3):
                    stem = f"{scene:03}_1.rf.{variant}"
                    for folder in ("images", "labels"):
                        (source / "train" / folder).mkdir(parents=True, exist_ok=True)
                    (source / "train/images" / (stem + ".jpg")).write_bytes(f"{scene}-{variant}".encode())
                    (source / "train/labels" / (stem + ".txt")).write_text("1 0.5 0.5 0.2 0.2\n1 0.5 0.5 0.2 0.2\n")
            (source / "train/labels/000_1.rf.0.txt").write_text("0 0.5 0.5 0.2 0.2\n")
            output = root / "prepared"
            with contextlib.redirect_stdout(io.StringIO()):
                prepare(source, output)
            report = json.loads((output / "manifest.json").read_text())
            self.assertEqual(report["excluded"]["ambiguous_class_images"], 1)
            scenes = {s: {r["scene"] for r in report["manifest"] if r["split"] == s} for s in ("train", "val", "test")}
            self.assertFalse(scenes["train"] & scenes["test"])
            self.assertFalse(scenes["train"] & scenes["val"])
            self.assertFalse(scenes["val"] & scenes["test"])
            for split in ("val", "test"):
                originals = [r["original"] for r in report["manifest"] if r["split"] == split]
                self.assertEqual(len(originals), len(set(originals)))
            for label in output.glob("labels/*/*.txt"):
                self.assertEqual(label.read_text().strip(), "0 0.50000000 0.50000000 0.20000000 0.20000000")
            with self.assertRaises(FileExistsError):
                prepare(source, output)


if __name__ == "__main__":
    unittest.main()
