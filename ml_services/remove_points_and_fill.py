#!/usr/bin/env python3
import numpy as np
import open3d as o3d
from pathlib import Path

def points_in_box_mask(points_xyz, box):
    x,y,z,dx,dy,dz,yaw = box
    pts = points_xyz - np.array([x,y,z], dtype=np.float32)
    c, s = np.cos(-yaw), np.sin(-yaw)
    R = np.array([[c,-s],[s,c]], dtype=np.float32)
    xy = pts[:, :2] @ R.T
    return (
        (np.abs(xy[:,0]) <= dx/2) &
        (np.abs(xy[:,1]) <= dy/2) &
        (np.abs(pts[:,2]) <= dz/2)
    )

def fill_bottom_face(box, grid=0.2, intensity=0.0):
    """Синтетическая «латка» на нижней грани бокса (равномерная сетка).
       Возвращает точки XYZI.
    """
    x,y,z,dx,dy,dz,yaw = box.astype(np.float32)
    z0 = z - dz/2
    nx = max(1, int(np.ceil(dx / grid)))
    ny = max(1, int(np.ceil(dy / grid)))
    xs = np.linspace(-dx/2, dx/2, nx)
    ys = np.linspace(-dy/2, dy/2, ny)
    xv, yv = np.meshgrid(xs, ys)
    xy_local = np.column_stack([xv.reshape(-1), yv.reshape(-1)])
    # поворот и перенос
    c, s = np.cos(yaw), np.sin(yaw)
    R = np.array([[c,-s],[s,c]], dtype=np.float32)
    xy_global = xy_local @ R.T + np.array([x,y], dtype=np.float32)
    X = xy_global[:,0]; Y = xy_global[:,1]
    Z = np.full_like(X, z0, dtype=np.float32)
    I = np.full_like(X, intensity, dtype=np.float32)
    return np.column_stack([X,Y,Z,I])

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("input_pcd", type=Path, help="original input .pcd")
    ap.add_argument("merged_npz", type=Path, help="merged_preds.npz (boxes,scores,labels)")
    ap.add_argument("--score_thr", type=float, default=0.2)
    ap.add_argument("--grid", type=float, default=0.2, help="patch grid on box bottom (m)")
    ap.add_argument("--out_pcd", type=Path, default=Path("data/cleaned_with_patches.pcd"))
    args = ap.parse_args()

    pcd = o3d.io.read_point_cloud(str(args.input_pcd))
    P3 = np.asarray(pcd.points, dtype=np.float32)
    I = np.zeros((len(P3),1), dtype=np.float32)

    data = np.load(args.merged_npz)
    boxes = data["boxes"]
    scores = data["scores"]

    m = scores >= args.score_thr
    boxes = boxes[m]

    # ⬇️ ДОБАВЬ ЭТО:
    boxes = np.asarray(boxes, dtype=np.float32)
    if boxes.ndim == 2 and boxes.shape[1] > 7:
        boxes = boxes[:, :7]  # берем только x,y,z,dx,dy,dz,yaw
    elif boxes.ndim == 1 and boxes.shape[0] > 7:
        boxes = boxes[:7][None, :]

    if boxes.size == 0:
        print("No boxes above threshold, saving original.")
        o3d.io.write_point_cloud(str(args.out_pcd), pcd)
        return

    # удалить точки внутри боксов
    keep = np.ones(len(P3), dtype=bool)
    for b in boxes:
        keep &= ~points_in_box_mask(P3, b)

    P3_out = P3[keep]
    I_out = I[keep]

    # «зашить» низ каждого бокса
    patches = []
    for b in boxes:
        patches.append(fill_bottom_face(b, grid=args.grid, intensity=0.0))
    if patches:
        patches_xyzi = np.vstack(patches).astype(np.float32)
        P3_out = np.vstack([P3_out, patches_xyzi[:, :3]])
        I_out = np.vstack([I_out, patches_xyzi[:, 3:4]])

    pcd_out = o3d.geometry.PointCloud()
    pcd_out.points = o3d.utility.Vector3dVector(P3_out)
    # (если хочешь — можно покрасить патчи отдельно в серый/белый через colors)
    o3d.io.write_point_cloud(str(args.out_pcd), pcd_out, write_ascii=False, compressed=True)
    print(f"Saved: {args.out_pcd}, points={len(P3_out)}")

if __name__ == "__main__":
    main()
