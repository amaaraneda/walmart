import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.validate_stock_annotations import measure_shelf, validate_dataset


class StockAnnotationTests(unittest.TestCase):
    def test_full_level_is_not_alert(self):
        shelf = {"roi": [[0, 0], [99, 0], [99, 99], [0, 99]], "gaps": []}
        self.assertEqual(measure_shelf(shelf, 100, 100)["occupancy_percent"], 100)
        self.assertFalse(measure_shelf(shelf, 100, 100)["low_stock_alert"])

    def test_large_gap_alerts(self):
        shelf = {"roi": [[0, 0], [99, 0], [99, 99], [0, 99]],
                 "gaps": [[[0, 0], [79, 0], [79, 99], [0, 99]]]}
        self.assertTrue(measure_shelf(shelf, 100, 100)["low_stock_alert"])

    def test_frontage_does_not_penalize_short_products(self):
        shelf = {"roi": [[0, 0], [99, 0], [99, 99], [0, 99]],
                 "gaps": [[[0, 0], [9, 0], [9, 49], [0, 49]]]}
        result = measure_shelf(shelf, 100, 100)
        self.assertEqual(result["occupancy_percent"], 90)
        self.assertEqual(result["area_occupancy_percent"], 95)

    def test_gap_outside_roi_rejected(self):
        shelf = {"roi": [[0, 0], [49, 0], [49, 99], [0, 99]],
                 "gaps": [[[40, 0], [60, 0], [60, 99], [40, 99]]]}
        with self.assertRaisesRegex(ValueError, "fuera de roi"):
            measure_shelf(shelf, 100, 100)

    def test_scene_leak_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "images").mkdir()
            (root / "annotations").mkdir()
            shelf = {"id": "n1", "visibility": "clear",
                     "roi": [[0, 0], [9, 0], [9, 9], [0, 9]], "gaps": []}
            for name, split in (("a", "train"), ("b", "test")):
                Image.new("RGB", (10, 10), "black" if name == "a" else "white").save(root / "images" / f"{name}.png")
                record = {"version": 1, "image": f"{name}.png", "scene_id": "misma-escena",
                          "split": split, "width": 10, "height": 10,
                          "review_status": "reviewed", "shelves": [shelf]}
                (root / "annotations" / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fuga de escena"):
                validate_dataset(root)

    def test_identical_images_with_different_scene_ids_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "images").mkdir()
            (root / "annotations").mkdir()
            shelf = {"id": "n1", "visibility": "clear",
                     "roi": [[0, 0], [9, 0], [9, 9], [0, 9]], "gaps": []}
            for name, split in (("a", "train"), ("b", "test")):
                Image.new("RGB", (10, 10), "white").save(root / "images" / f"{name}.png")
                record = {"version": 1, "image": f"{name}.png", "scene_id": name,
                          "split": split, "width": 10, "height": 10,
                          "review_status": "reviewed", "shelves": [shelf]}
                (root / "annotations" / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "imágenes idénticas"):
                validate_dataset(root)


if __name__ == "__main__":
    unittest.main()
