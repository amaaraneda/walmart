import base64
import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend import app as app_module
from backend.coverage import Box


class FakeDetector:
    ready = True
    metadata = {}

    def predict(self, image):
        return [Box(0, 0, image.width * 0.2, image.height, 0.9)]


class UntrainedDetector:
    ready = False


class FrontDetector:
    ready = True
    metadata = {}

    def predict(self, image):
        width, height = image.size
        boxes = [Box(x * width / 1000, .1 * height, (x + 80) * width / 1000,
                     .36 * height, .9) for x in (0, 90, 180, 270, 360, 450, 540, 630, 720, 810, 920)]
        boxes += [Box(x * width / 1000, .56 * height, (x + 40) * width / 1000,
                      .8 * height, .9) for x in (50, 110, 170)]
        return boxes


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app_module.app)
        image = Image.new("RGB", (100, 100), "white")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        self.image = buffer.getvalue()

    def test_missing_checkpoint_is_explicit(self):
        with patch.object(app_module, "companion_detector", UntrainedDetector()):
            response = self.client.post("/api/analyze", files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 503)

    def test_health_lists_both_models(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["id"] for item in response.json()["models"]}, {"principal", "companero"})
        self.assertEqual(response.json()["models"][0]["id"], "companero")

    def test_companion_is_default(self):
        with patch.object(app_module, "companion_detector", FakeDetector()):
            response = self.client.post("/api/analyze", files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["model_id"], "companero")

    def test_void_candidates_are_explicit_and_never_trigger_alert(self):
        with patch.object(app_module, "companion_detector", FakeDetector()), patch.object(app_module, "void_candidate_detector", FakeDetector()):
            response = self.client.post("/api/analyze", data={"include_void_candidates": "true"},
                                        files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["void_candidate_requested"])
        self.assertEqual(payload["void_candidate_detections"], 1)
        self.assertIsNone(payload["occupancy_percent"])
        self.assertIsNone(payload["low_stock_alert"])

    def test_requested_void_candidate_must_exist(self):
        with patch.object(app_module, "companion_detector", FakeDetector()), patch.object(app_module, "void_candidate_detector", UntrainedDetector()):
            response = self.client.post("/api/analyze", data={"include_void_candidates": "true"},
                                        files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 503)

    def test_companion_model_can_be_selected(self):
        with patch.object(app_module, "companion_detector", FakeDetector()):
            response = self.client.post("/api/analyze", data={"model_id": "companero"}, files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["model_id"], "companero")
        self.assertEqual(response.json()["detections"], 1)
        self.assertIsNone(response.json()["occupancy_percent"])

    def test_unknown_model_is_rejected(self):
        response = self.client.post("/api/analyze", data={"model_id": "otro"}, files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 422)

    def test_product_detections_do_not_invent_empty_stock(self):
        image = Image.new("RGB", (800, 400), "white")
        draw = ImageDraw.Draw(image)
        boxes = []
        for top, bottom in ((70, 180), (240, 350)):
            for x in (80, 120, 160, 200):
                draw.rectangle((x, top, x + 22, bottom - 5), fill="blue")
                boxes.append(Box(x, top, x + 22, bottom - 5, .9))
            draw.rectangle((50, bottom, 750, bottom + 4), fill="black")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        with patch.object(app_module, "companion_detector", FakeDetector()), patch.object(FakeDetector, "predict", return_value=boxes):
            response = self.client.post("/api/analyze", files={"image": ("test.jpg", buffer.getvalue(), "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["detections"], len(boxes))
        self.assertEqual(payload["visible_detections"], len(boxes))
        self.assertEqual(payload["high_confidence_detections"], len(boxes))
        self.assertEqual(len(payload["product_detections"]), len(boxes))
        self.assertIsNone(payload["occupancy_percent"])
        self.assertIsNone(payload["low_stock_alert"])
        self.assertFalse(payload["threshold_applied"])
        self.assertEqual(payload["empty_regions"], [])
        self.assertTrue(base64.b64decode(payload["annotated_image"].split(",", 1)[1]))

    def test_zero_detections_does_not_claim_empty_shelf(self):
        with patch.object(app_module, "companion_detector", FakeDetector()), patch.object(FakeDetector, "predict", return_value=[]):
            response = self.client.post("/api/analyze", files={"image": ("test.jpg", self.image, "image/jpeg")})
        payload = response.json()
        self.assertTrue(payload["review_required"])
        self.assertIsNone(payload["occupancy_percent"])
        self.assertIsNone(payload["low_stock_alert"])
        self.assertEqual(payload["empty_regions"], [])

    def test_reports_experimental_percent_without_operational_alert(self):
        image = Image.new("RGB", (1000, 500), "white")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        with patch.object(app_module, "companion_detector", FrontDetector()):
            response = self.client.post("/api/analyze", files={"image": ("front.jpg", buffer.getvalue(), "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload["occupancy_percent"], float)
        self.assertEqual(len(payload["shelves"]), 2)
        self.assertTrue(payload["low_stock_candidate"])
        self.assertIsNone(payload["low_stock_alert"])
        self.assertFalse(payload["threshold_applied"])

    def test_medium_confidence_product_is_visible(self):
        predictions = [Box(10, 10, 35, 60, .3), Box(50, 10, 75, 60, .8)]
        with patch.object(app_module, "companion_detector", FakeDetector()), patch.object(FakeDetector, "predict", return_value=predictions):
            response = self.client.post("/api/analyze", files={"image": ("test.jpg", self.image, "image/jpeg")})
        payload = response.json()
        self.assertEqual(payload["visible_detections"], 2)
        self.assertEqual(payload["high_confidence_detections"], 1)

    def test_bad_threshold_rejected(self):
        with patch.object(app_module, "companion_detector", FakeDetector()):
            response = self.client.post("/api/analyze", data={"threshold": "120"}, files={"image": ("test.jpg", self.image, "image/jpeg")})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
