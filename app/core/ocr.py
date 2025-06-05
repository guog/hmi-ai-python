# ocr.py: OCR功能模块，封装了PaddleOCR的初始化与图片文字识别接口
import io
from typing import Optional

import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

from app.core.image2hmi import calculate_area

# 全局只初始化一次OCR模型，避免重复加载
ocr_models: dict[str, PaddleOCR] = {}


def get_ocr(lang: str = "ch"):
  """
  获取指定语言的OCR模型实例,若未初始化则新建。
  :param lang: 语言代码，如'ch'表示中文
  :return: PaddleOCR实例
  """
  if lang not in ocr_models:
    ocr_models[lang] = PaddleOCR(use_angle_cls=True, lang=lang)
  return ocr_models[lang]


def ocr_to_json(image_bytes: bytes, lang: Optional[str] = "ch"):
  """
  对输入图片字节流进行OCR识别,返回识别结果列表。
  :param image_bytes: 图片的二进制内容
  :param lang: 语言代码，默认为中文(ch), 可选'en'表示英文
  :return: 识别结果，包含文本、置信度和文本框坐标
  """
  image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
  image_np = np.array(image)
  ocr_result = ocr(image_np, lang)
  result = []
  for item in ocr_result:
    for box, text in item:
      x1, y1 = box[0]
      x2, y2 = box[2]
      payload = {"text": text[0]}
      origin = {
        "name": text[0],  # 识别出的文本内容
        "confidence": text[1],  # 置信度分数
        "x1": x1,  # 文本框左上角x坐标
        "y1": y1,  # 文本框左上角y坐标
        "x2": x2,  # 文本框右下角x坐标
        "y2": y2,  # 文本框右下角y坐标
      }
      attrs = calculate_area(x1, y1, x2, y2)
      result.append(
        {
          "payload": payload,
          "origin": origin,
          "attrs": attrs,
          "createdAt": f"{np.datetime64('now').astype(str)}",
        }
      )
  return result


def ocr(image_np: np.ndarray, lang: Optional[str] = "ch"):
  """
  对输入的图像进行OCR识别,返回识别结果。
  :param image_np: 输入图像的numpy数组
  :param lang: 语言代码，默认为中文(ch), 可选'en'表示英文
  :return: OCR识别结果
  """
  ocr_engine = get_ocr(lang)
  ocr_result = ocr_engine.ocr(image_np, cls=True)
  return ocr_result
