"""
Convert images to HMI format (router layer).
"""

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.image2hmi import (
  HMIEventGenerator,
  ImageValidator,
  SymbolMapper,
  YoloModel,
)
from app.core.ocr import ocr
from app.core.settings import settings

router = APIRouter()

# 依赖注入/单例
symbol_mapper = SymbolMapper(settings.SYMBOL_MAPPING_PATH)
model = YoloModel(settings.MODEL_PATH)
line_model = YoloModel(settings.MODEL_LINE_PATH)
event_generator = HMIEventGenerator(symbol_mapper)


@router.post("/image2hmi")
async def image2hmi(
  file: UploadFile = File(..., description="上传的文件"),
  lang: Optional[str] = "ch",
  no_ocr: Optional[bool] = False,
  no_symbol: Optional[bool] = False,
  no_line: Optional[bool] = False,
):
  """
  将上传的图片转换为HMI格式。
  Args:
      file: 上传的图片文件
      lang: 默认中文'ch',可选'en'表示英文,
        'fr'表示法文, 'german'表示德文, 'korean'表示韩文, 'japan'表示日文
        完整语言列表请参考PaddleOCR文档:
        https://paddlepaddle.github.io/PaddleOCR/v2.10.0/ppocr/blog/multi_languages.html#5
      no_ocr: 是否跳过OCR识别, 默认为False
      no_symbol: 是否跳过符号识别, 默认为False
      no_line: 是否跳过线条识别, 默认为False
  Returns:
      StreamingResponse: 服务器发送事件(SSE)流
  """

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
    if no_symbol:
      symbol_results = []
    else:
      symbol_results = model.predict(img)
    if no_line:
      line_results = []
    else:
      line_results = line_model.predict(img)
    if no_ocr:
      text_results = []
    else:
      text_results = ocr(img, lang=lang)
  except Exception as e:
    raise HTTPException(500, f"模型推理失败: {str(e)}")
  return StreamingResponse(
    event_generator.generate(
      symbol_results, line_results, text_results, fileInfo, lang
    ),
    media_type="text/event-stream",
  )
