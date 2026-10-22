import unittest
from pathlib import Path

from backend.prepare_void_dataset import assign, scene_id


class VoidDatasetTests(unittest.TestCase):
    def test_augmented_variants_keep_same_scene(self):
        first = Path("IMG-20250318-WA0009_jpg.rf.aaa.jpg")
        second = Path("IMG-20250318-WA0009_jpg.rf.bbb.jpg")
        self.assertEqual(scene_id(first), scene_id(second))

    def test_split_is_reproducible_and_scene_disjoint(self):
        groups = {f"scene-{number}": [] for number in range(20)}
        first = assign(groups)
        self.assertEqual(first, assign(groups))
        self.assertEqual(set(first.values()), {"train", "val", "test"})
        self.assertEqual(len(first), len(groups))


if __name__ == "__main__":
    unittest.main()
