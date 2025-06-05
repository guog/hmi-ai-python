"""
Core logic for image to HMI conversion.
"""

import json
import re
from asyncio import sleep
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from .settings import settings

# 配置常量
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg"]
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


class SymbolMapper:
  def __init__(self, mapping_path: Path):
    self.mapping = self._load_mapping(mapping_path)

  def _load_mapping(self, path: Path) -> dict:
    try:
      with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    except Exception as e:
      print(f"加载符号映射文件失败: {e}")
      return {}

  def to_hmi_symbol(self, name: str) -> Optional[Any]:
    flag = self.mapping.get(name, None)
    if flag is None:
      print(f"未找到名称: {name}")
    return flag


class YoloModel:
  def __init__(self, model_path: Path):
    self.model = YOLO(model_path)

  def predict(self, img: np.ndarray) -> List[Results]:
    return self.model.predict(source=img, verbose=False)


class ImageValidator:
  @staticmethod
  def validate_file(file) -> None:
    if file.content_type.lower() not in ALLOWED_MIME_TYPES:
      raise ValueError("仅支持 JPG/PNG 格式图片")
    file_extension = re.split(r"\.", file.filename)[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
      raise ValueError("文件扩展名无效")

  @staticmethod
  def read_image_bytes(content: bytes) -> np.ndarray:
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
      raise ValueError("无法解码图片")
    return img


class HMIEventGenerator:
  """生成HMI事件的异步生成器。
  用于处理YOLO和PaddleOCR的识别结果，并生成HMI符号和文本事件。
  """

  def __init__(self, symbol_mapper: SymbolMapper):
    self.symbol_mapper = symbol_mapper

  async def generate(
    self,
    symbol_results: List[Results],
    line_results: List[Results],
    text_results: List[Results],
    fileInfo: dict,
    lang: Optional[str] = "ch",
  ):
    """
    生成HMI事件的异步生成器。
    Args:
      symbol_results (List[Results]): YOLO识别的符号结果。
      line_results (List[Results]): YOLO识别的线条结果。
      text_results (List[Results]): PaddleOCR识别的文本结果。
      fileInfo (dict): 包含文件信息的字典，如文件名、类型等。
      lang (Optional[str]): 语言选项，默认中文'ch',可选'en'表示英文,
        'fr'表示法文, 'german'表示德文, 'korean'表示韩文, 'japan'表示日文
    Yields:
      str: 生成的事件字符串，包含识别的符号、线条和文本信息。
    """

    yield "event: start\ndata: 开始图片分析任务\n\n"
    msg = (
      f"收到用户发送的图片{fileInfo['filename']}, "
      f"我需要识别这个图片中的内容, "
      f"转换为 HMI 符号, 并在当前图纸上绘制出来."
    )
    yield f"event: message\ndata: {msg}\n\n"

    await sleep(settings.SERVER_SEND_EVENTS_INTERVAL)
    yield "event: message\ndata: 开始绘制:\n\n"
    index = 0

    async def process_yolo_results(
      results: List[Results], result_type: str, symbol_mapper: SymbolMapper
    ):
      """
      处理YOLO识别结果的生成器。
      Args:
        results (List[Results]): YOLO识别结果列表。
        result_type (str): 事件类型，默认为"symbol"或"line"。
      Yields:
        str: 生成的事件字符串，包含识别的符号或线条信息。
      """
      # Use `nonlocal index` to share the `index`
      #   variable across nested functions, allowing
      #   it to track the sequence of processed items
      #   globally within the generator.
      nonlocal index
      for item in results:
        for box in item.boxes:
          await sleep(settings.SERVER_SEND_EVENTS_INTERVAL)
          cls = box.cls.item()
          cls_name = item.names[int(cls)]
          payload = symbol_mapper.to_hmi_symbol(cls_name)
          if payload is None:
            continue
          x1, y1, x2, y2 = box.xyxy[0].tolist()
          attrs = calculate_area(x1, y1, x2, y2)
          conf = box.conf.item()
          index += 1
          yield f"event: message\ndata: {index}. {cls_name} <br />\n\n"
          await sleep(settings.SERVER_SEND_EVENTS_INTERVAL)
          yield (
            f"event: {result_type}\ndata: "
            + json.dumps(
              {
                "payload": payload,
                "origin": {
                  "name": cls_name,
                  "confidence": conf,
                  "x1": x1,
                  "y1": y1,
                  "x2": x2,
                  "y2": y2,
                },
                "attrs": attrs,
                "createdAt": f"{datetime.now().isoformat()}",
              },
              ensure_ascii=False,
            )
            + "\n\n"
          )

    async def process_paddleocr_results(
      results: list, result_type: str = "text"
    ):
      """处理PaddleOCR识别结果的生成器。
      Args:
        results (list): PaddleOCR识别结果列表。
        result_type (str): 事件类型，默认为"text"。
      Yields:
        str: 生成的事件字符串，包含识别的文本和相关信息。
      """
      # Use `nonlocal index` to share the `index`
      #   variable across nested functions, allowing
      #   it to track the sequence of processed items
      nonlocal index
      for item in results:
        for box, content in item:
          if len(content) < 2:
            continue
          if len(box) < 4:
            continue

          await sleep(settings.SERVER_SEND_EVENTS_INTERVAL)
          x1, y1 = box[0]
          x2, y2 = box[2]
          confidence = content[1]
          text = content[0].strip()
          if not text:
            continue
          payload = {"text": text}
          origin = {
            "name": text,  # 识别出的文本内容
            "confidence": confidence,  # 置信度分数
            "x1": x1,  # 文本框左上角x坐标
            "y1": y1,  # 文本框左上角y坐标
            "x2": x2,  # 文本框右下角x坐标
            "y2": y2,  # 文本框右下角y坐标
          }
          attrs = calculate_area(x1, y1, x2, y2)
          index += 1
          yield f"event: message\ndata: {index}. 文字: {text} <br />\n\n"
          await sleep(settings.SERVER_SEND_EVENTS_INTERVAL)
          yield (
            f"event: {result_type}\ndata: "
            + json.dumps(
              {
                "payload": payload,
                "origin": origin,
                "attrs": attrs,
                "createdAt": f"{datetime.now().isoformat()}",
              },
              ensure_ascii=False,
            )
            + "\n\n"
          )

    async for msg in process_yolo_results(
      symbol_results, "symbol", self.symbol_mapper
    ):
      yield msg

    async for msg in process_yolo_results(
      line_results, "line", self.symbol_mapper
    ):
      yield msg

    async for msg in process_paddleocr_results(text_results, "text"):
      yield msg

    yield "event: done\ndata: 图片分析完成\n\n"


def calculate_area(
  x1: float, y1: float, x2: float, y2: float
) -> Dict[str, int]:
  """
  根据矩形的左上角和右下角坐标计算其宽度和高度。

  参数:
    x1 (float): 左上角的 X 坐标。
    y1 (float): 左上角的 Y 坐标。
    x2 (float): 右下角的 X 坐标。
    y2 (float): 右下角的 Y 坐标。

  返回:
    Dict[str, int]: 包含以下键值的字典:
      - "x": 左上角的 X 坐标 (int)
      - "y": 左上角的 Y 坐标 (int)
      - "width": 矩形的宽度 (int)
      - "height": 矩形的高度 (int)
  """
  return {
    "x": int(x1),
    "y": int(y1),
    "width": abs(int(x2) - int(x1)),
    "height": abs(int(y2) - int(y1)),
  }
