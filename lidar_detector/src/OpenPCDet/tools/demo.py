import argparse
import os
import glob
from pathlib import Path

try:
    import open3d
    from visual_utils import open3d_vis_utils as V
    OPEN3D_FLAG = True
except:
    import mayavi.mlab as mlab
    from visual_utils import visualize_utils as V
    OPEN3D_FLAG = False

import numpy as np
import torch

from pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets.dataset import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils


class DemoDataset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin'):
        """
        Args:
            root_path:
            dataset_cfg:
            class_names:
            training:
            logger:
        """
        super().__init__(
            dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
        )
        self.root_path = root_path
        self.ext = ext
        data_file_list = glob.glob(str(root_path / f'*{self.ext}')) if self.root_path.is_dir() else [self.root_path]

        data_file_list.sort()
        self.sample_file_list = data_file_list

    def __len__(self):
        return len(self.sample_file_list)

    def __getitem__(self, index):
        if self.ext == '.bin':
            raw = np.fromfile(self.sample_file_list[index], dtype=np.float32)
            if raw.size == 0:
                return None  # пустой файл пропускаем

            cols = 5 if raw.size % 5 == 0 else 4
            pts = raw.reshape(-1, cols)
            if cols == 4:
                ts = np.zeros((pts.shape[0], 1), dtype=np.float32)  # фиктивный timestamp
                points = np.hstack([pts, ts]).astype(np.float32)
            else:
                points = pts.astype(np.float32)

        elif self.ext == '.npy':
            points = np.load(self.sample_file_list[index]).astype(np.float32)
            # при необходимости довести до 5 каналов:
            if points.shape[1] == 4:
                ts = np.zeros((points.shape[0], 1), dtype=np.float32)
                points = np.hstack([points, ts])

        else:
            raise NotImplementedError

        # ВНИМАНИЕ: центрирование убрали.
        # Тайлы уже сохранены в локальных координатах в pcd2tiles.py,
        # повторный сдвиг здесь ломает сопоставление с meta.jsonl.

        input_dict = {'points': points, 'frame_id': index}
        data_dict = self.prepare_data(data_dict=input_dict)

        # если после препроцессинга вдруг пусто — пропускаем сэмпл
        if data_dict is None or ('voxels' in data_dict and getattr(data_dict['voxels'], 'shape', [0])[0] == 0):
            return None
        return data_dict



def parse_config():
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('--cfg_file', type=str, default='cfgs/kitti_models/second.yaml',
                        help='specify the config for demo')
    parser.add_argument('--data_path', type=str, default='demo_data',
                        help='specify the point cloud data file or directory')
    parser.add_argument('--ckpt', type=str, default=None, help='specify the pretrained model')
    parser.add_argument('--ext', type=str, default='.bin', help='specify the extension of your point cloud data file')

    args = parser.parse_args()

    cfg_from_yaml_file(args.cfg_file, cfg)

    return args, cfg



def main():
    args, cfg = parse_config()
    logger = common_utils.create_logger()
    logger.info('-----------------Quick Demo of OpenPCDet-------------------------')

    demo_dataset = DemoDataset(
        dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, training=False,
        root_path=Path(args.data_path), ext=args.ext, logger=logger
    )
    logger.info(f'Total number of samples: 	{len(demo_dataset)}')

    model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=demo_dataset)
    model.load_params_from_file(filename=args.ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()

    # === Headless-safe: where to save outputs ===
    import os, numpy as np
    out_dir = Path(os.environ.get('OPCDET_OUT', '../data/opencdet_cubes/preds'))
    out_dir.mkdir(parents=True, exist_ok=True)

    def to_cpu_np(x):
        import torch
        if hasattr(x, "detach"):
            x = x.detach()
        if hasattr(x, "cpu"):
            x = x.cpu()
        return np.asarray(x)

    saved = 0
    with torch.no_grad():
        for idx in range(len(demo_dataset)):
            data_dict = demo_dataset[idx]
            if data_dict is None:
                logger.info(f'[INFO] Skip empty/filtered sample #{idx}')
                continue

            batch = demo_dataset.collate_batch([data_dict])
            load_data_to_gpu(batch)

            try:
                pred_dicts, _ = model.forward(batch)
            except Exception as e:
                logger.warning(f'[WARN] Skip sample #{idx} due to RuntimeError: {e}')
                continue

            pd = pred_dicts[0]
            
            # сохраняем с реальным идентификатором файла (совпадёт с meta.jsonl)
            sid = Path(demo_dataset.sample_file_list[idx]).stem  # например "000123"
            save_path = out_dir / f"sample_{sid}.npz"

            np.savez_compressed(
                save_path,
                points=to_cpu_np(batch['points']),          # [N, 5] с batch_idx в [:,0]
                boxes=to_cpu_np(pd.get('pred_boxes', [])),  # [M, 7]
                scores=to_cpu_np(pd.get('pred_scores', [])),
                labels=to_cpu_np(pd.get('pred_labels', [])),
                sample_id=sid
            )
            saved += 1
            logger.info(f"[SAVED] {save_path}")

    logger.info(f'Demo done. Saved {saved} sample(s).')




if __name__ == '__main__':
    main()