#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Разрезает входной PCD на продолговатые тайлы вдоль траектории,
центрирует каждый тайл (для OpenPCDet), сохраняет:
  data/opencdet_cubes/testing/velodyne/000000.bin  (KITTI xyzi, intensity=1)
  data/opencdet_cubes/testing/velodyne/000000.npy  (локальные XYZ...)
  data/opencdet_cubes/testing/velodyne/meta.jsonl  ({"id": "000000", "origin": [ox,oy,oz]})
  data/opencdet_cubes/ImageSets/test.txt           (список id)
Траектория оценивается как медиана Y по X-бинам (как в твоём ноутбуке).
"""

import os, json
from pathlib import Path
import argparse
import numpy as np
import open3d as o3d


def build_center_line_xy(points_xy: np.ndarray, bin_size: float) -> np.ndarray:
    """Строим грубую центральную линию дороги: для каждого X-интервала берём медиану Y."""
    xy = points_xy
    order = np.argsort(xy[:, 0])
    xy_sorted = xy[order]
    x_min, x_max = xy_sorted[:, 0].min(), xy_sorted[:, 0].max()

    xs, ys = [], []
    x_bins = np.arange(x_min, x_max, bin_size, dtype=float)
    for xb in x_bins:
        mask = (xy_sorted[:, 0] >= xb) & (xy_sorted[:, 0] < xb + bin_size)
        if np.any(mask):
            y_med = np.median(xy_sorted[mask, 1])
            xs.append(xb + bin_size / 2.0)
            ys.append(y_med)
    if not xs:
        return np.empty((0, 2), dtype=np.float32)
    return np.column_stack([xs, ys]).astype(np.float32)


def create_cubes_along_trajectory(points_xyz: np.ndarray,
                                  center_line_xy: np.ndarray,
                                  tile_len: float,
                                  half_width: float,
                                  step: float) -> list[np.ndarray]:
    """Режем на «длинные» прямоугольные тайлы вдоль линии.
    tile_len — длина тайла вдоль траектории
    half_width — половина ширины по нормали
    step — шаг смещения окна по линии (может быть < tile_len для перекрытия)
    """
    cubes = []
    if len(center_line_xy) < 2:
        return cubes

    half_len = tile_len / 2.0
    # идём по узлам линии с шагом, выраженным в количестве вершин
    # перевод step (в метрах) в «кол-во вершин» условно: пройдём всю ломаную накопленной длиной
    segs = np.diff(center_line_xy, axis=0)
    seg_len = np.linalg.norm(segs, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])  # длина вдоль линии в метрах
    total = cum[-1]
    if total == 0:
        return cubes

    positions = np.arange(half_len, total - half_len + 1e-6, step, dtype=float)

    # вспомогательные функции
    def point_on_polyline(pos_m: float) -> tuple[np.ndarray, np.ndarray]:
        """Точка и касательная на ломаной при длине pos_m от начала."""
        # находим сегмент
        idx = np.searchsorted(cum, pos_m, side="right") - 1
        idx = np.clip(idx, 0, len(segs) - 1)
        seg_start = center_line_xy[idx]
        seg_vec = segs[idx]
        seg_len_i = seg_len[idx]
        t = (pos_m - cum[idx]) / max(seg_len_i, 1e-9)
        pt = seg_start + t * seg_vec
        dir_v = seg_vec / max(seg_len_i, 1e-9)
        return pt, dir_v

    xy = points_xyz[:, :2]
    for pos in positions:
        center, direction = point_on_polyline(pos)
        normal = np.array([-direction[1], direction[0]], dtype=np.float32)
        rel = xy - center  # (N,2)

        mask = (
            (np.abs(rel @ direction) <= half_len) &
            (np.abs(rel @ normal) <= half_width)
        )
        if np.any(mask):
            cubes.append(points_xyz[mask])

    return cubes


def to_kitti_bin(points_xyz_any: np.ndarray) -> bytes:
    """KITTI .bin: float32 [x,y,z,intensity]. Если I нет — ставим 1."""
    pts = np.asarray(points_xyz_any, dtype=np.float32)
    xyz = pts[:, :3].astype(np.float32)
    i = np.ones((len(xyz), 1), dtype=np.float32)
    xyzi = np.concatenate([xyz, i], axis=1)
    return xyzi.tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcd_path", type=Path, help="входной PCD")
    ap.add_argument("--out_root", type=Path, default=Path("data/opencdet_cubes"))
    ap.add_argument("--bin_size", type=float, default=50.0, help="шаг бинов по X для оценки линии")
    ap.add_argument("--tile_len", type=float, default=108.0, help="длина тайла вдоль траектории")
    ap.add_argument("--half_width", type=float, default=54.0, help="половина ширины тайла")
    ap.add_argument("--step", type=float, default=90.0, help="шаг между центрами тайлов")
    ap.add_argument("--center_mode", choices=["tile_center", "points_mean", "none"],
                    default="tile_center",
                    help="какой origin вычитать перед сохранением .bin")
    args = ap.parse_args()

    VEL_DIR = args.out_root / "testing" / "velodyne"
    IMGSETS = args.out_root / "ImageSets"
    META_PATH = VEL_DIR / "meta.jsonl"
    VEL_DIR.mkdir(parents=True, exist_ok=True)
    IMGSETS.mkdir(parents=True, exist_ok=True)
    if META_PATH.exists():
        META_PATH.unlink()

    # читаем облако
    pcd = o3d.io.read_point_cloud(str(args.pcd_path))
    pts = np.asarray(pcd.points, dtype=np.float32)
    if pts.size == 0:
        raise RuntimeError("PCD пустой.")

    # строим центр-линию
    center_line = build_center_line_xy(pts[:, :2], bin_size=args.bin_size)
    cubes = create_cubes_along_trajectory(
        points_xyz=pts, center_line_xy=center_line,
        tile_len=args.tile_len, half_width=args.half_width, step=args.step
    )

    id_list = []
    with META_PATH.open("w", encoding="utf-8") as mf:
        for i, cube in enumerate(cubes):
            base = f"{i:06d}"
            bin_path = VEL_DIR / f"{base}.bin"
            npy_path = VEL_DIR / f"{base}.npy"

            # origin для обратного возврата боксов в глобальные координаты
            if args.center_mode in ("tile_center", "points_mean"):
                cx, cy, cz = cube[:, 0].mean(), cube[:, 1].mean(), cube[:, 2].mean()
            else:
                cx, cy, cz = 0.0, 0.0, 0.0
            origin = np.array([cx, cy, cz], dtype=np.float32)

            # центрируем координаты перед сохранением (ожидание модели)
            cube_loc = cube.copy()
            cube_loc[:, :3] -= origin[None, :]

            with open(bin_path, "wb") as f:
                f.write(to_kitti_bin(cube_loc))
            np.save(npy_path, cube_loc)

            id_list.append(base)
            mf.write(json.dumps({"id": base, "origin": origin.tolist()}, ensure_ascii=False) + "\n")

    with (IMGSETS / "test.txt").open("w") as f:
        for bid in id_list:
            f.write(bid + "\n")

    print(f"Сохранено тайлов: {len(id_list)} → {VEL_DIR}")
    print(f"meta.jsonl: {META_PATH}")


if __name__ == "__main__":
    main()
