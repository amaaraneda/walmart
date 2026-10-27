import unittest

import numpy as np

from backend.gaps import extract_gap_regions


class GapPostprocessingTests(unittest.TestCase):
    def test_retains_large_high_probability_region(self):
        probability = np.zeros((200, 300), dtype=np.float32)
        probability[40:120, 90:190] = .95
        mask, regions = extract_gap_regions(probability)
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0]["left"], 90)
        self.assertGreater(mask.sum(), 7000)

    def test_rejects_small_or_low_probability_regions(self):
        probability = np.zeros((200, 300), dtype=np.float32)
        probability[20:25, 20:25] = .99
        probability[50:130, 90:190] = .59
        mask, regions = extract_gap_regions(probability)
        self.assertEqual(regions, [])
        self.assertEqual(int(mask.sum()), 0)


if __name__ == "__main__":
    unittest.main()
