#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полный пайплайн OpenPCDet:
1. pcd → bin-тайлы
2. инференс модели
3. объединение предсказаний
4. удаление точек внутри боксов

Запускать: poetry run python run_full_pipeline.py --pcd ../data/points.pcd --ckpt ../data/voxelnext_nuscenes_kernel1.pth
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

THIS_DIR = Path(__file__).resolve().parent      # OpenPCDet/
ROOT_DIR = THIS_DIR.parent                      # на уровень выше (где pcd2tiles.py и data/)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run(cmd, cwd=None, env=None):
    log(f"📦 Запуск: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        raise SystemExit(f"❌ Ошибка: {' '.join(map(str, cmd))} (code={result.returncode})")
    log("✅ Успешно завершено.\n")

def main(img_storage: str, file_name: str):
    
    src_file = os.path.join(img_storage, file_name)
    clean_file_name = os.path.splitext(file_name)[0]
    result_file = os.path.join(img_storage, f"cleaned_{clean_file_name}.pcd")
    boxes_file = os.path.join(img_storage, f"boxes_{clean_file_name}.npz")
    boxes_file_json = boxes_file.replace(".npz", ".json")
    
    
    parser = argparse.ArgumentParser("Полный пайплайн OpenPCDet")
    parser.add_argument("--pcd", default=str(src_file), help="Входной PCD")
    parser.add_argument("--ckpt", default=str(ROOT_DIR / "data" / "voxelnext_nuscenes_kernel1.pth"), help="Чекпойнт модели")
    parser.add_argument("--out_root", default=str(ROOT_DIR / "data" / "opencdet_cubes"), help="Папка для тайлов")
    parser.add_argument("--merged_npz", default=str(boxes_file))
    parser.add_argument("--clean_pcd", default=str(result_file))

    # параметры разбиения
    parser.add_argument("--bin_size", type=int, default=50)
    parser.add_argument("--tile_len", type=int, default=108)
    parser.add_argument("--half_width", type=int, default=54)
    parser.add_argument("--step", type=int, default=90)

    # параметры модели
    parser.add_argument("--cfg", default=str(ROOT_DIR / "data" / "cbgs_voxel0075_voxelnext.yaml"))
    parser.add_argument("--ext", default=".bin")

    # параметры фильтрации
    parser.add_argument("--score_thr", type=float, default=0.20)
    parser.add_argument("--grid", type=float, default=0.20)

    args = parser.parse_args([])

    # пути
    pcd2tiles_py = ROOT_DIR / "pcd2tiles.py"
    merge_py = ROOT_DIR / "merge_npz_preds.py"
    remove_py = ROOT_DIR / "remove_points_and_fill.py"
    velodyne_dir = Path(args.out_root) / "testing" / "velodyne"
    preds_dir = Path(args.out_root) / "preds"

    # 1️⃣ Разбиение pcd на тайлы
    log("🚀 Шаг 1: Разбиение исходного PCD на тайлы (.bin)")
    run([
        sys.executable, str(pcd2tiles_py),
        str(args.pcd),
        "--out_root", str(args.out_root),
        "--bin_size", str(args.bin_size),
        "--tile_len", str(args.tile_len),
        "--half_width", str(args.half_width),
        "--step", str(args.step)
    ], cwd=THIS_DIR)

    # 2️⃣ Инференс модели
    log("🚀 Шаг 2: Запуск модели OpenPCDet на тайлах")
    os.environ["OPCDET_OUT"] = str(preds_dir)
    run([
        sys.executable, str(THIS_DIR / "tools" / "demo.py"),
        "--cfg_file", str(args.cfg),
        "--ckpt", str(args.ckpt),
        "--data_path", str(velodyne_dir),
        "--ext", args.ext
    ], cwd=THIS_DIR)

    # 3️⃣ Объединение предсказаний
    log("🚀 Шаг 3: Объединение всех предсказаний в один файл")
    run([
        sys.executable, str(merge_py),
        "--preds_dir", str(preds_dir),
        "--out", str(args.merged_npz)
    ], cwd=THIS_DIR)

    # 4️⃣ Удаление точек внутри боксов
    log("🚀 Шаг 4: Удаление точек внутри боксов и зашивка дна")
    run([
        sys.executable, str(remove_py),
        str(args.pcd),
        str(args.merged_npz),
        "--score_thr", str(args.score_thr),
        "--grid", str(args.grid),
        "--out_pcd", str(args.clean_pcd)
    ], cwd=THIS_DIR)

    log("🎉 Пайплайн завершён успешно!")
    log(f"📁 Итоговый очищенный PCD: {args.clean_pcd}")
    log(f"📁 Объединённые предсказания: {args.merged_npz}")
    
    result = {
        "result_filename": result_file,
        "boxes_json_filename": boxes_file_json
    }

    return result

if __name__ == "__main__":
    main()
