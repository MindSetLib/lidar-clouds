#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Считывает все sample_*.npz из каталога предсказаний,
по meta.jsonl восстанавливает глобальные координаты боксов,
(опционально) делает простой BEV-NMS-заглушку,
сохраняет объединённые: merged_preds.npz (+ параллельно merged_preds.json).
"""

from pathlib import Path
import argparse
import json
import re
import numpy as np


SID_RE = re.compile(r"sample_(\d+)\.npz$")


def load_meta(meta_path: Path) -> dict[str, np.ndarray]:
    origins: dict[str, np.ndarray] = {}
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            origins[str(rec["id"])] = np.array(rec["origin"], dtype=np.float32)
    return origins


def bev_nms_placeholder(boxes: np.ndarray, scores: np.ndarray, iou_thr: float = 0.5) -> np.ndarray:
    """Простейшая заглушка (сортировка по score). Поменяй на реальный NMS при необходимости."""
    order = np.argsort(-scores)
    return order.astype(int)


def save_json(boxes: np.ndarray, scores: np.ndarray, labels: np.ndarray, out_json: Path):
    out_json.parent.mkdir(parents=True, exist_ok=True)
    items = []
    for b, s, l in zip(boxes, scores, labels):
        b = b.tolist()
        items.append({
            "center": [float(b[0]), float(b[1]), float(b[2])],
            "size":   [float(b[3]), float(b[4]), float(b[5])],
            "yaw":    float(b[6]),
            "score":  float(s),
            "label":  int(l),
        })
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {out_json} (boxes={len(items)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds_dir", type=Path, default=Path("data/opencdet_cubes/preds"))
    ap.add_argument("--out", type=Path, default=Path("data/opencdet_cubes/merged_preds.npz"))
    ap.add_argument("--json", type=Path, default=None, help="путь для JSON; по умолчанию рядом с NPZ")
    ap.add_argument("--meta", type=Path, default=None,
                    help="путь к meta.jsonl; по умолчанию ищется в ../testing/velodyne/meta.jsonl от preds_dir")
    ap.add_argument("--nms", action="store_true", help="включить простую NMS-заглушку")
    args = ap.parse_args()

    preds_dir = args.preds_dir.resolve()
    if args.meta is None:
        args.meta = (preds_dir.parent / "testing" / "velodyne" / "meta.jsonl").resolve()
    if not args.meta.exists():
        raise FileNotFoundError(f"meta.jsonl not found: {args.meta}")

    origins = load_meta(args.meta)

    boxes_all, scores_all, labels_all = [], [], []
    pts_any = None

    npz_list = sorted(preds_dir.glob("sample_*.npz"))
    if not npz_list:
        raise RuntimeError(f"В {preds_dir} не найдено sample_*.npz")

    for npz_path in npz_list:
        d = np.load(npz_path, allow_pickle=True)
        if "boxes" not in d or d["boxes"].size == 0:
            continue

        boxes = np.asarray(d["boxes"], dtype=np.float32)
        if boxes.ndim == 2 and boxes.shape[1] > 7:
            boxes = boxes[:, :7]

        # восстановим sample_id
        if "sample_id" in d:
            sid = str(d["sample_id"])
        else:
            m = SID_RE.search(npz_path.name)
            sid = m.group(1) if m else None
        if sid is None or sid not in origins:
            raise RuntimeError(f"Не удалось найти origin для {npz_path} (sample_id={sid})")

        origin = origins[sid]  # (3,)
        boxes[:, :3] += origin[None, :]  # перевод в глобальные координаты

        scores = np.asarray(d["scores"], dtype=np.float32) if "scores" in d else np.ones(len(boxes), np.float32)
        labels = np.asarray(d["labels"], dtype=np.int32) if "labels" in d else np.zeros(len(boxes), np.int32)

        boxes_all.append(boxes)
        scores_all.append(scores)
        labels_all.append(labels)

        if pts_any is None and "points" in d:
            pts_any = d["points"]

    if not boxes_all:
        raise RuntimeError("После объединения нет ни одного бокса.")

    boxes = np.concatenate(boxes_all, axis=0)
    scores = np.concatenate(scores_all, axis=0)
    labels = np.concatenate(labels_all, axis=0)

    if args.nms and len(boxes) > 0:
        keep = bev_nms_placeholder(boxes, scores, iou_thr=0.5)
        boxes, scores, labels = boxes[keep], scores[keep], labels[keep]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, boxes=boxes, scores=scores, labels=labels, points=pts_any)
    print(f"Saved NPZ:  {args.out} (boxes={len(boxes)})")

    out_json = args.json if args.json is not None else args.out.with_suffix(".json")
    save_json(boxes, scores, labels, out_json)


if __name__ == "__main__":
    main()
