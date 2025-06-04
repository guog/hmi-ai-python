from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.ocr import ocr_image

router = APIRouter()


@router.post("/ocr")
async def ocr_endpoint(
  file: UploadFile = File(...),
  lang: Optional[str] = "ch",
):
  """
  用PaddleOCR对上传图片进行文字识别。
  Args:
      file: 上传的图片文件
      lang: PaddleOCR语言模型,默认中文'ch',可选'en'表示英文,
        'fr'表示法文, 'german'表示德文, 'korean'表示韩文, 'japan'表示日文
  Returns:
      JSON格式返回识别结果
  """
  if not file.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="文件必须为图片类型。")
  try:
    image_bytes = await file.read()
    text_results = ocr_image(image_bytes, lang)
    return text_results
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")
