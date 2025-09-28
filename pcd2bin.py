#!/usr/bin/env python3
"""
Convert a single .pcd file to a single .bin file for OpenPCDet demo.
Usage:
    python pcd2bin.py input.pcd output.bin [--time]
"""

import sys
import numpy as np
import open3d as o3d
from pathlib import Path

def pcd_to_bin(input_pcd: Path, output_bin: Path, with_time: bool = False):
    # 1. читаем pcd через open3d
    pc = o3d.io.read_point_cloud(str(input_pcd))
    pts = np.asarray(pc.points, dtype=np.float32)
    if pts.size == 0:
        raise ValueError(f"Файл {input_pcd} не содержит точек!")

    # 2. добавляем нули для intensity (+ timestamp, если нужно)
    intensity = np.zeros((pts.shape[0], 1), dtype=np.float32)
    if with_time:
        ts = np.zeros((pts.shape[0], 1), dtype=np.float32)
        arr = np.hstack([pts, intensity, ts])  # XYZI + T
    else:
        arr = np.hstack([pts, intensity])      # XYZI

    # 3. сохраняем как float32 бинарник
    arr.tofile(output_bin)
    print(f"[OK] Saved {arr.shape[0]} points ({arr.shape[1]} dims) → {output_bin}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    with_time = "--time" in sys.argv

    if not in_path.exists():
        sys.exit(f"❌ Файл {in_path} не найден")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pcd_to_bin(in_path, out_path, with_time)
