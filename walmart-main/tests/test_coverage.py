import unittest

from backend.coverage import Box, estimate_occupancy, union_length, measure_shelf_front


class CoverageTests(unittest.TestCase):
    def test_union_does_not_double_count(self):
        self.assertEqual(union_length([(0, 30), (20, 70)]), 70)

    def test_threshold_is_strictly_below(self):
        boxes = [Box(0, 0, 30, 100, 0.8)]
        self.assertEqual(estimate_occupancy(boxes, 100, 100), 30)
        self.assertFalse(estimate_occupancy(boxes, 100, 100) < 30)

    def test_empty_region(self):
        self.assertEqual(estimate_occupancy([], 100, 100), 0)

    def test_clips_and_unions(self):
        boxes = [Box(-10, 0, 20, 100, 0.8), Box(10, 0, 40, 100, 0.9)]
        self.assertEqual(estimate_occupancy(boxes, 100, 100), 40)

    def test_headroom_does_not_penalize_full_shelf(self):
        result = measure_shelf_front([Box(0, 75, 100, 100, .9)], 100, 100)
        self.assertEqual(result["occupancy_percent"], 100)
        self.assertEqual(result["empty_regions"], [])

    def test_visible_gap_and_overlap(self):
        result = measure_shelf_front([Box(0, 60, 30, 100, .9), Box(20, 50, 40, 100, .9), Box(70, 80, 100, 100, .9)], 100, 100)
        self.assertEqual(result["occupancy_percent"], 70)
        self.assertEqual(result["empty_percent"], 30)
        self.assertEqual([(r["x1"], r["x2"]) for r in result["empty_regions"]], [(40, 70)])

    def test_edge_gaps_are_included(self):
        result = measure_shelf_front([Box(20, 0, 80, 100, .9)], 100, 100)
        self.assertEqual(result["occupancy_percent"], 60)
        self.assertEqual(len(result["empty_regions"]), 2)

    def test_no_detections_is_unknown(self):
        result = measure_shelf_front([], 100, 100)
        self.assertIsNone(result["occupancy_percent"])
        self.assertTrue(result["review_required"])


if __name__ == "__main__":
    unittest.main()
