# 0) Предварительно

* Драйвер NVIDIA и **CUDA 11.7** (nvcc 11.7).
* Python **3.9** (важно для совместимости PyTorch/спец.опов).
* Git, C/C++ toolchain.

Проверка:

```bash
nvcc --version   # должен показать 11.7.x
python3.9 -V     # 3.9.x
```

---

# 1) Создаём окружение через Poetry

```bash
# в любой рабочей директории
poetry new lidar-clouds
cd lidar-clouds

# выставляем python 3.9 (если не подтянулся автоматически)
poetry env use python3.9
```

Создайте/замените `pyproject.toml` (минимально нужное):

```toml
[tool.poetry]
name = "lidar-clouds"
version = "0.1.0"
description = "PCD → тайлы → OpenPCDet → merge → постобработка"
authors = ["you <you@example.com>"]
readme = "README.md"
packages = [{include = "lidar_clouds"}]

[tool.poetry.dependencies]
python = ">=3.9,<3.10"
# Пины под CUDA 11.7 и NumPy<2 для совместимости со сборками
numpy = "1.26.4"
scikit-image = "0.21.0"
open3d = "^0.18.0"     # опционально (можно убрать, если не нужен)
matplotlib = "^3.8.0"
tqdm = "^4.66.0"
easydict = "^1.13"
tensorboardX = "^2.6"
pyyaml = "^6.0"

# spconv для cu117 (готовые бинарные колёса)
spconv-cu117 = "2.3.6"

# SciPy лучше притянуть заранее, чтобы не конфликтовал
scipy = "^1.11.4"

# Скриптам
plotly = "^5.22.0"

[tool.poetry.group.dev.dependencies]
ipykernel = "^6.29.0"

# Источник PyTorch (CUDA 11.7)
[[tool.poetry.source]]
name = "pytorch-cu117"
url = "https://download.pytorch.org/whl/cu117"
priority = "supplemental"
```

Устанавливаем зависимости (кроме самого PyTorch пока):

```bash
poetry install
```

Теперь ставим **PyTorch 2.0.1 + cu117** (и совместимые torchvision/torchaudio). Проще сделать это через pip внутри окружения Poetry:

```bash
poetry run python -m pip install \
  torch==2.0.1+cu117 \
  torchvision==0.15.2+cu117 \
  torchaudio==2.0.2+cu117 \
  --index-url https://download.pytorch.org/whl/cu117
```

Проверка:

```bash
poetry run python - <<'PY'
import torch
print("torch:", torch.__version__, "cuda:", torch.version.cuda)
PY
```

Ожидаемо: `torch 2.0.1+cu117 cuda 11.7`.

---

# 2) Клонируем и ставим OpenPCDet

```bash
# из корня проекта (где pyproject.toml)
git clone https://github.com/open-mmlab/OpenPCDet.git
cd OpenPCDet
```

Установка в editable-режиме под уже установленный torch/cuda (важно отключить build isolation):

```bash
poetry run python -m pip install -e . --no-build-isolation
```

> Если соберутся `pcdet/ops/*` без ошибок — ок.
> Если увидите жалобы на NumPy 2.x ABI — убедитесь, что `numpy==1.26.4` и повторите команду.

---

# 3) Патч `tools/demo.py`

Ваша текущая версия уже очень близка. Сделайте **две правки**:

1. **Убрать центрирование** точек в `DemoDataset.__getitem__` (мы уже центрируем тайлы при сохранении `.bin`).
2. Сохранение результатов — по **настоящему `sample_id`** (stem входного файла) и с полем `sample_id` внутри `.npz`.

Мини-диф (куда и что убрать/добавить):

```diff
--- a/tools/demo.py
+++ b/tools/demo.py
@@ -51,20 +51,6 @@ class DemoDataset(DatasetTemplate):
         else:
             raise NotImplementedError

-        # --- Центрирование УБРАТЬ ---
-        pc_range = np.array(cfg.DATA_CONFIG.POINT_CLOUD_RANGE, dtype=np.float32)
-        window_center = (pc_range[:3] + pc_range[3:]) / 2.0
-        mins = points[:, :3].min(0)
-        maxs = points[:, :3].max(0)
-        data_center = (mins + maxs) / 2.0
-        shift = data_center - window_center
-        points[:, :3] -= shift
-
         input_dict = {'points': points, 'frame_id': index}
         data_dict = self.prepare_data(data_dict=input_dict)
@@ -122,7 +108,11 @@ def main():
             except Exception as e:
                 logger.warning(f'[WARN] Skip sample #{idx} due to RuntimeError: {e}')
                 continue
-            pd = pred_dicts[0]
-            save_path = out_dir / f"sample_{idx:06d}.npz"
+            pd  = pred_dicts[0]
+            sid = Path(demo_dataset.sample_file_list[idx]).stem  # "000123"
+            save_path = out_dir / f"sample_{sid}.npz"
             np.savez_compressed(
                 save_path,
                 points=to_cpu_np(batch['points']),
                 boxes=to_cpu_np(pd.get('pred_boxes', [])),
                 scores=to_cpu_np(pd.get('pred_scores', [])),
-                labels=to_cpu_np(pd.get('pred_labels', []))
+                labels=to_cpu_np(pd.get('pred_labels', [])),
+                sample_id=sid
             )
```

Сохраните файл.

---

# 4) Положите вспомогательные скрипты в корень (рядом с `OpenPCDet/`)

Вы уже использовали их — разместите **рядом с каталогом** `OpenPCDet`:

* `pcd2tiles.py` — нарезка `points.pcd` на тайлы (`.bin`) + `meta.jsonl` с origin.
* `merge_npz_preds.py` — склейка `sample_*.npz` из `preds/` в **глобальные** боксы + JSON.
* `remove_points_and_fill.py` — удаление точек внутри боксов + «зашивка» нижней грани (при необходимости).
* (опционально) `pcd2bin.py` — конверт отдельного `.pcd → .bin` (KITTI xyzi).

> Если нужно — я пришлю эти файлы «целиком» ещё раз. В предыдущих шагах мы уже согласовали их содержимое (включая запись `meta.jsonl` и `sample_id`).

---

# 5) Пример запуска всего пайплайна

Предположим структура:

```
project/
  pyproject.toml
  OpenPCDet/
  data/
    points.pcd
    voxelnext_nuscenes_kernel1.pth
```

## 5.1 Нарезка PCD в тайлы (из `OpenPCDet/` мы не запускаем — команда из корня проекта)

```bash
poetry run python pcd2tiles.py data/points.pcd \
  --out_root data/opencdet_cubes \
  --bin_size 50 --tile_len 108 --half_width 54 --step 90
```

Результат:

```
data/opencdet_cubes/testing/velodyne/000000.bin (.npy)
data/opencdet_cubes/testing/velodyne/meta.jsonl
data/opencdet_cubes/ImageSets/test.txt
```

## 5.2 Инференс OpenPCDet (из папки **OpenPCDet/**)

```bash
cd OpenPCDet

poetry run python tools/demo.py \
  --cfg_file tools/cfgs/nuscenes_models/cbgs_voxel0075_voxelnext.yaml \
  --ckpt ../data/voxelnext_nuscenes_kernel1.pth \
  --data_path ../data/opencdet_cubes/testing/velodyne \
  --ext .bin
```

Результат: `../data/opencdet_cubes/preds/sample_000000.npz` и т.д.
(В headless-среде Open3D ругнётся — это нормально; наши правки сохраняют `.npz` и пропускают показ окна.)

## 5.3 Склейка предсказаний в глобальные координаты (+ JSON)

```bash
cd ..

poetry run python merge_npz_preds.py \
  --preds_dir data/opencdet_cubes/preds \
  --out data/opencdet_cubes/merged_preds.npz
# Параллельно будет записан data/opencdet_cubes/merged_preds.json
```

## 5.4 (Опционально) Удаление точек внутри боксов + «зашивка» низа

```bash
poetry run python remove_points_and_fill.py \
  data/points.pcd \
  data/opencdet_cubes/merged_preds.npz \
  --score_thr 0.20 \
  --grid 0.20 \
  --out_pcd data/points_cleaned.pcd
```

## 5.5 (Опционально) Конвертация в PLY для CloudCompare

```bash
poetry run python - <<'PY'
import open3d as o3d
pcd = o3d.io.read_point_cloud("data/points_cleaned.pcd")
o3d.io.write_point_cloud("data/points_cleaned.ply", pcd)
print("saved: data/points_cleaned.ply")
PY
```

## 5.6 BEV-визуализация (вид сверху) и PNG

```python
# ноутбучная ячейка (poetry run jupyter, либо просто python -c ...)

pcd_path    = "data/points.pcd"
preds_path  = "data/opencdet_cubes/merged_preds.npz"
png_out     = "data/bev_overlay.png"

# ... вставьте сниппет BEV-визуализации из моего прошлого ответа ...
```

---

# 6) Requirements (альтернатива poetry)

Если хотите быстро развернуть через `pip`:

`requirements.txt`

```
numpy==1.26.4
scipy==1.11.4
scikit-image==0.21.0
open3d==0.18.0
matplotlib==3.8.0
tqdm==4.66.0
easydict==1.13
tensorboardX==2.6
PyYAML==6.0
plotly==5.22.0
spconv-cu117==2.3.6
```

А затем PyTorch:

```bash
python -m pip install -r requirements.txt
python -m pip install \
  torch==2.0.1+cu117 torchvision==0.15.2+cu117 torchaudio==2.0.2+cu117 \
  --index-url https://download.pytorch.org/whl/cu117

# и потом
cd OpenPCDet
python -m pip install -e . --no-build-isolation
```

---

## Важные замечания по совместимости

* **NumPy 1.26.4** — многие бинарные колёса (torchvision, ops OpenPCDet) собирались под 1.x; NumPy 2.0 часто даёт ABI-конфликты.
* **spconv-cu117==2.3.6** стабильно работает с torch 2.0.1+cu117.
* Если у вас валится рендер Open3D (headless), это **не мешает** — мы сохраняем `.npz` и пропускаем визуализацию.
* Если в каком-то тайле **нет точек** внутри диапазона `POINT_CLOUD_RANGE` модели — demo пропустит сэмпл. Это нормально (дорожные тайлы могут быть пустыми для детектора объектов).

