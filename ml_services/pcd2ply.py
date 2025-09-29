#!/usr/bin/env python3
import argparse
import open3d as o3d
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Конвертация PCD → PLY")
    parser.add_argument("input_pcd", type=str, help="Путь к входному .pcd файлу")
    parser.add_argument("output_ply", type=str, nargs="?", help="Путь к выходному .ply файлу (опционально)")
    args = parser.parse_args()

    input_path = Path(args.input_pcd)
    if not input_path.exists():
        raise FileNotFoundError(f"Файл {input_path} не найден")

    # Если не указан output — сохраняем рядом с тем же именем
    output_path = Path(args.output_ply) if args.output_ply else input_path.with_suffix(".ply")

    print(f"[INFO] Чтение: {input_path}")
    pcd = o3d.io.read_point_cloud(str(input_path))
    print(f"[INFO] Сохранение в: {output_path}")
    o3d.io.write_point_cloud(str(output_path), pcd)
    print("[✅] Конвертация завершена успешно.")

if __name__ == "__main__":
    main()
