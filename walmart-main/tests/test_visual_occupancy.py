import unittest

from backend.coverage import Box
from backend.visual_occupancy import estimate_visual_occupancy


class VisualOccupancyTests(unittest.TestCase):
    def test_no_products_is_unknown_not_zero_stock(self):
        result = estimate_visual_occupancy([], 1000, 500)
        self.assertIsNone(result["occupancy_percent"])

    def test_sparse_front_does_not_shrink_denominator(self):
        boxes = [Box(x, 50, x + 80, 180, .9) for x in (0, 90, 180, 270, 360, 450, 540, 630, 720, 810, 920)]
        boxes += [Box(x, 280, x + 40, 400, .9) for x in (50, 110, 170)]
        result = estimate_visual_occupancy(boxes, 1000, 500)
        self.assertEqual(len(result["shelves"]), 2)
        self.assertGreater(result["shelves"][0]["occupancy_percent"], 80)
        self.assertLess(result["shelves"][1]["occupancy_percent"], 30)
        self.assertTrue(result["shelves"][1]["low_stock_candidate"])
        self.assertIsNone(result["shelves"][1]["low_stock_alert"])

    def test_unframed_crop_is_unknown(self):
        boxes = [Box(x, 50, x + 40, 180, .9) for x in (200, 250, 300, 350, 400)]
        result = estimate_visual_occupancy(boxes, 1000, 500)
        self.assertIsNone(result["occupancy_percent"])
        self.assertEqual(result["reason"], "shelf_width_not_observable")


if __name__ == "__main__":
    unittest.main()
