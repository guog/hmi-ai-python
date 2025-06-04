"""
Core logic for image to HMI conversion.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

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
  def __init__(self, symbol_mapper: SymbolMapper):
    self.symbol_mapper = symbol_mapper

  async def generate(self, results: List[Results], fileInfo: dict):
    yield "event: start\ndata: 开始图片分析任务\n\n"
    msg = (
      f"收到用户发送的图片{fileInfo['filename']}, "
      f"我需要识别这个图片中的内容, "
      f"转换为 HMI 符号, 并在当前图纸上绘制出来."
    )
    yield f"event: message\ndata: {msg}\n\n"
    from asyncio import sleep

    await sleep(0.2)
    yield "event: message\ndata: 开始绘制:\n\n"
    index = 0
    for item in results:
      for box in item.boxes:
        await sleep(0.2)
        cls = box.cls.item()
        cls_name = item.names[int(cls)]
        payload = self.symbol_mapper.to_hmi_symbol(cls_name)
        if payload is None:
          continue
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        attrs = calculate_area(x1, y1, x2, y2)
        conf = box.conf.item()
        index += 1
        yield f"event: message\ndata: {index}. {cls_name} <br />\n\n"
        await sleep(0.2)
        yield f"event: symbol\ndata: {
          json.dumps(
            {
              'payload': payload,
              'origin': {
                'name': cls_name,
                'confidence': conf,
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
              },
              'attrs': attrs,
              'createdAt': f'{datetime.now().isoformat()}',
            },
            ensure_ascii=False,
          )
        }\n\n"
    yield "event: done\ndata: 图片分析任务完成\n\n"


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
