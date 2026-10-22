"""Segmentación experimental de huecos visibles en góndolas.

La red predice píxeles anotados como vacío, no ausencia de cajas de productos.
Se carga sólo un state_dict generado por este proyecto (weights_only=True).
"""

from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = ROOT / "artifacts/models/gap-unet.pt"
SIZE = 320


class ConvBlock(nn.Sequential):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


class GapUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.down1 = ConvBlock(3, 16)
        self.down2 = ConvBlock(16, 32)
        self.down3 = ConvBlock(32, 64)
        self.bridge = ConvBlock(64, 128)
        self.pool = nn.MaxPool2d(2)
        self.up3 = ConvBlock(128 + 64, 64)
        self.up2 = ConvBlock(64 + 32, 32)
        self.up1 = ConvBlock(32 + 16, 16)
        self.output = nn.Conv2d(16, 1, 1)

    def forward(self, x):
        a = self.down1(x)
        b = self.down2(self.pool(a))
        c = self.down3(self.pool(b))
        d = self.bridge(self.pool(c))
        d = nn.functional.interpolate(d, size=c.shape[-2:], mode="bilinear", align_corners=False)
        d = self.up3(torch.cat((d, c), dim=1))
        d = nn.functional.interpolate(d, size=b.shape[-2:], mode="bilinear", align_corners=False)
        d = self.up2(torch.cat((d, b), dim=1))
        d = nn.functional.interpolate(d, size=a.shape[-2:], mode="bilinear", align_corners=False)
        return self.output(self.up1(torch.cat((d, a), dim=1)))


def image_tensor(image: Image.Image) -> torch.Tensor:
    resized = image.convert("RGB").resize((SIZE, SIZE), Image.Resampling.BILINEAR)
    return torch.from_numpy(np.asarray(resized).copy()).permute(2, 0, 1).float() / 255


class GapSegmenter:
    def __init__(self, weights: Path = DEFAULT_WEIGHTS):
        self.weights = weights
        self._model = None

    @property
    def ready(self) -> bool:
        return self.weights.is_file()

    def predict(self, image: Image.Image) -> np.ndarray:
        if not self.ready:
            raise FileNotFoundError(self.weights)
        if self._model is None:
            self._model = GapUNet().eval()
            self._model.load_state_dict(torch.load(self.weights, map_location="cpu", weights_only=True))
        with torch.inference_mode():
            logits = self._model(image_tensor(image)[None])
            probability = logits.sigmoid()[0, 0].numpy()
        return np.asarray(
            Image.fromarray((probability * 255).astype(np.uint8)).resize(image.size, Image.Resampling.BILINEAR),
            dtype=np.float32,
        ) / 255
