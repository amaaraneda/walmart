import unittest

from backend.coverage import Box
from backend.tiled_detection import merge_boxes


class TiledDetectionTests(unittest.TestCase):
    def test_suppresses_duplicate_without_merging_neighbors(self):
        original = Box(0, 0, 20, 20, .9)
        duplicate = Box(1, 1, 21, 21, .7)
        neighbor = Box(22, 0, 42, 20, .8)
        self.assertEqual(merge_boxes([duplicate, neighbor, original]), [original, neighbor])


if __name__ == "__main__":
    unittest.main()
