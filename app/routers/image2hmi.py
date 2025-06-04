"""
Convert images to HMI format (router layer).
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.image2hmi import (
  HMIEventGenerator,
  ImageValidator,
  SymbolMapper,
  YoloModel,
)
from app.core.settings import settings

router = APIRouter()

# 依赖注入/单例
symbol_mapper = SymbolMapper(settings.SYMBOL_MAPPING_PATH)
model = YoloModel(settings.MODEL_PATH)
line_model = YoloModel(settings.MODEL_LINE_PATH)
event_generator = HMIEventGenerator(symbol_mapper)


@router.post("/image2hmi")
async def image2hmi(file: UploadFile = File(..., description="上传的文件")):
  try:
    ImageValidator.validate_file(file)
  except ValueError as e:
    raise HTTPException(400, str(e))
  fileInfo = {
    "filename": file.filename,
    "content_type": file.content_type,
    "size": getattr(file, "size", None),
  }
  try:
    content = await file.read()
  except Exception as e:
    raise HTTPException(500, f"文件读取失败: {str(e)}")
  try:
    img = ImageValidator.read_image_bytes(content)
  except Exception as e:
    raise HTTPException(400, f"图像解码失败: {str(e)}")
  try:
    results = model.predict(img)
    line_results = line_model.predict(img)
    results.extend(line_results)
  except Exception as e:
    raise HTTPException(500, f"模型推理失败: {str(e)}")
  return StreamingResponse(
    event_generator.generate(results, fileInfo), media_type="text/event-stream"
  )
