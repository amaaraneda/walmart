"""Adaptación parcial: cajas de producto locales son píxeles no vacíos.

No supone que el fondo no etiquetado sea vacío. No sustituye las máscaras de
vacío del dominio objetivo; reduce falsos positivos sobre envases conocidos.
"""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from .gap_model import GapUNet, SIZE, image_tensor
from .train_gaps import DATA, GapDataset, evaluate, pairs, loss_function


ROOT = Path(__file__).resolve().parents[1]


class ProductInteriorDataset(Dataset):
    def __init__(self, split: str):
        folder = ROOT / "data/shelf_products_v2"
        images = sorted((folder / "images" / split).glob("*.jpg"))
        # Unas pocas variantes por escena evitan dominar la adaptación.
        seen = {}
        self.entries = []
        for photo in images:
            scene = photo.name.split("_")[0]
            if seen.get(scene, 0) >= 4:
                continue
            label = folder / "labels" / split / (photo.stem + ".txt")
            if label.is_file():
                self.entries.append((photo, label))
                seen[scene] = seen.get(scene, 0) + 1

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, index):
        photo, label = self.entries[index]
        with Image.open(photo) as source:
            image = image_tensor(source)
        interior = np.zeros((SIZE, SIZE), dtype=np.float32)
        for line in label.read_text(encoding="utf-8").splitlines():
            values = line.split()
            if len(values) < 5:
                continue
            _, cx, cy, w, h = map(float, values[:5])
            # Sólo la parte central del producto es un negativo confiable.
            x1 = max(0, round((cx - w * .35) * SIZE))
            x2 = min(SIZE, round((cx + w * .35) * SIZE))
            y1 = max(0, round((cy - h * .35) * SIZE))
            y2 = min(SIZE, round((cy + h * .35) * SIZE))
            interior[y1:y2, x1:x2] = 1
        return image, torch.from_numpy(interior)[None]


def overlap_rate(model, loader):
    wrong = total = 0
    model.eval()
    with torch.inference_mode():
        for image, product in loader:
            prediction = model(image).sigmoid() >= .6
            wrong += torch.logical_and(prediction, product > 0).sum().item()
            total += (product > 0).sum().item()
    return round(wrong / max(total, 1), 4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()
    random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(4)
    public = pairs("Train")
    random.shuffle(public)
    val, train = public[:round(len(public)*.2)], public[round(len(public)*.2):]
    public_train = DataLoader(GapDataset(train, augment=True), batch_size=4, shuffle=True, num_workers=0)
    public_val = DataLoader(GapDataset(val), batch_size=4, num_workers=0)
    public_test = DataLoader(GapDataset(pairs("Test")), batch_size=4, num_workers=0)
    local_train = DataLoader(ProductInteriorDataset("train"), batch_size=4, shuffle=True, num_workers=0)
    local_val = DataLoader(ProductInteriorDataset("val"), batch_size=4, num_workers=0)
    local_test = DataLoader(ProductInteriorDataset("test"), batch_size=4, num_workers=0)
    model = GapUNet()
    model.load_state_dict(torch.load(args.initial, map_location="cpu", weights_only=True))
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0002, weight_decay=.0001)
    best_score = -1.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(1, args.epochs+1):
        model.train()
        product_batches = iter(local_train)
        losses = []
        for image, target in public_train:
            try:
                local_image, product = next(product_batches)
            except StopIteration:
                product_batches = iter(local_train)
                local_image, product = next(product_batches)
            optimizer.zero_grad()
            supervised = loss_function(model(image), target)
            local_logits = model(local_image)
            negative = torch.nn.functional.binary_cross_entropy_with_logits(local_logits, torch.zeros_like(local_logits), reduction="none")
            negative = (negative * product).sum() / product.sum().clamp_min(1)
            loss = supervised + .3 * negative
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        metrics = evaluate(model, public_val)
        wrong = overlap_rate(model, local_val)
        score = metrics["iou"] - wrong
        print(f"epoch={epoch} loss={np.mean(losses):.4f} public_val_iou={metrics['iou']:.4f} local_product_fp={wrong:.4f}", flush=True)
        if score > best_score:
            best_score = score
            torch.save(model.state_dict(), args.output)
    model.load_state_dict(torch.load(args.output, map_location="cpu", weights_only=True))
    report = {"public_train": len(train), "local_train": len(local_train.dataset), "public_validation": evaluate(model, public_val), "public_test": evaluate(model, public_test), "local_product_false_positive_val": overlap_rate(model, local_val), "local_product_false_positive_test": overlap_rate(model, local_test), "caveat": "Sin máscaras de vacíos locales: no hay recall ni precisión de huecos para el dominio del proyecto."}
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
