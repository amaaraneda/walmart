"""Entrena y evalúa un segmentador de huecos con máscaras públicas locales.

Uso: python -m backend.train_gaps --epochs 12. El conjunto Test nunca se
utiliza para selección de época ni umbral.
"""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from .gap_model import DEFAULT_WEIGHTS, GapUNet, SIZE, image_tensor


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/gap_detection_public"


def pairs(split: str):
    result = []
    for source in ("GroZi-120", "WebMarket"):
        folder = DATA / source / split
        for photo in sorted((folder / "Images").glob("*.jpg")):
            mask = folder / "Masks" / (photo.stem + ".tiff")
            if mask.is_file():
                result.append((photo, mask, source))
    return result


class GapDataset(Dataset):
    def __init__(self, entries, augment=False):
        self.entries = entries
        self.augment = augment

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, index):
        photo, mask, _ = self.entries[index]
        with Image.open(photo) as src, Image.open(mask) as annotation:
            image = image_tensor(src)
            target = torch.from_numpy((np.asarray(annotation.resize((SIZE, SIZE), Image.Resampling.NEAREST)) > 127).astype(np.float32).copy())[None]
        if self.augment and random.random() < .5:
            image, target = image.flip(-1), target.flip(-1)
        if self.augment:
            image = (image * random.uniform(.8, 1.2) + random.uniform(-.08, .08)).clamp(0, 1)
        return image, target


def loss_function(logits, target):
    bce = torch.nn.functional.binary_cross_entropy_with_logits(logits, target)
    probability = logits.sigmoid()
    intersection = (probability * target).sum(dim=(1, 2, 3))
    dice = 1 - ((2 * intersection + 1) / (probability.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3)) + 1)).mean()
    return bce + dice


def evaluate(model, loader):
    totals = np.zeros(4, dtype=np.float64)  # TP, FP, FN, TN
    model.eval()
    with torch.inference_mode():
        for image, target in loader:
            predicted = model(image).sigmoid() >= .5
            truth = target >= .5
            totals += [torch.logical_and(predicted, truth).sum().item(), torch.logical_and(predicted, ~truth).sum().item(), torch.logical_and(~predicted, truth).sum().item(), torch.logical_and(~predicted, ~truth).sum().item()]
    tp, fp, fn, tn = totals
    return {"iou": round(float(tp / max(tp + fp + fn, 1)), 4), "precision": round(float(tp / max(tp + fp, 1)), 4), "recall": round(float(tp / max(tp + fn, 1)), 4), "pixel_accuracy": round(float((tp + tn) / max(totals.sum(), 1)), 4)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--output", type=Path, default=DEFAULT_WEIGHTS)
    args = parser.parse_args()
    random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(4)
    train_entries = pairs("Train")
    test_entries = pairs("Test")
    if len(train_entries) < 20 or len(test_entries) < 20:
        raise ValueError("Faltan imágenes o máscaras en data/gap_detection_public")
    random.shuffle(train_entries)
    split = round(len(train_entries) * .2)
    validation, training = train_entries[:split], train_entries[split:]
    train_loader = DataLoader(GapDataset(training, augment=True), batch_size=4, shuffle=True, num_workers=0)
    val_loader = DataLoader(GapDataset(validation), batch_size=4, num_workers=0)
    test_loader = DataLoader(GapDataset(test_entries), batch_size=4, num_workers=0)
    model = GapUNet()
    optimizer = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.0001)
    best = -1.
    best_epoch = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(1, args.epochs + 1):
        model.train()
        losses = []
        for image, target in train_loader:
            optimizer.zero_grad()
            loss = loss_function(model(image), target)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        metrics = evaluate(model, val_loader)
        print(f"epoch={epoch} loss={np.mean(losses):.4f} val_iou={metrics['iou']:.4f} val_precision={metrics['precision']:.4f} val_recall={metrics['recall']:.4f}", flush=True)
        if metrics["iou"] > best:
            best = metrics["iou"]
            best_epoch = epoch
            torch.save(model.state_dict(), args.output)
    model.load_state_dict(torch.load(args.output, map_location="cpu", weights_only=True))
    report = {"source": "gapDetection/gapDetectionDatasets", "train_images": len(training), "val_images": len(validation), "test_images": len(test_entries), "best_epoch": best_epoch, "validation": evaluate(model, val_loader), "test": evaluate(model, test_loader), "size": SIZE}
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
