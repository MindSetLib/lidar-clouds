from typing import Optional
import uuid
import logging
from pathlib import Path
import uvicorn
from services import PCDService
from ocr_configurations import Config, setup_logging

import redis
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse

logger = setup_logging()

app = FastAPI(
    title="PCD API",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

STORAGE_DIR = Path(Config.IMG_STORAGE)
rds = redis.from_url(Config.REDIS_URL, decode_responses=True)
pcd_service = PCDService(STORAGE_DIR, rds)


@app.post("/api/upload_pcd",
          tags=["PCD"],
          description="Загрузка PCD файла и постановка в очередь")
async def upload_pcd(file: UploadFile):
    """Прием PCD файла от фронта. UID генерируется на бэке."""
    # --- проверка расширения ---
    if not file.filename.lower().endswith(".pcd"):
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть в формате .pcd"
        )

    uid = uuid.uuid4().hex
    try:
        file_path = pcd_service.save_file(file, uid)
        pcd_service.enqueue(file_path, uid)
        pcd_service.set_status(
            uid=uid,
            status="processing",
            src_filename=file.filename,
            result_filename=None,
            boxes=[]
        )
    except Exception as exc:
        logger.exception("Ошибка загрузки PCD")
        raise HTTPException(status_code=500,
                            detail="Ошибка при сохранении файла") from exc

    return JSONResponse({"uid": uid, "status": "processing"})


@app.get("/api/status",
         tags=["PCD"],
         description="Проверка статуса обработки PCD")
async def get_status(uid: str):
    """Возврат статуса или имени готового файла."""
    try:
        status = pcd_service.get_status(uid)
    except Exception as exc:
        logger.exception("Ошибка Redis для uid=%s", uid)
        raise HTTPException(status_code=500,
                            detail="Не удалось получить статус") from exc

    if status is None:
        raise HTTPException(status_code=404, detail="UID не найден")

    if status == "ready":
        result_name = f"cleaned_{uid}.pcd"
        return JSONResponse({"uid": uid, "status": status,
                             "result_file": result_name})
    return JSONResponse({"uid": uid, "status": status})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
