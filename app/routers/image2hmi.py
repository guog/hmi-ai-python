"""
Convert images to HMI format.
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from ultralytics.engine.results import Results

router = APIRouter()

# 允许的 MIME 类型和文件扩展名
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg"]
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# 模型路径
MODEL_PATH = Path(__file__).parent.parent.parent / "models/hollysys-hmi.pt"
# HMI 符号映射文件路径
SYMBOL_MAPPING_PATH = (
  Path(__file__).parent.parent.parent / "hmi-symbol-mapping.json"
)

try:
  with open(
    SYMBOL_MAPPING_PATH,
    "r",
    encoding="utf-8",
  ) as file:
    SYMBOL_NAME_MAPPING = json.load(file)
except FileNotFoundError:
  print("错误: 找不到 hmi-symbol-mapping.json 文件！")
except json.JSONDecodeError:
  print("错误: JSON 文件格式不正确！")
except TypeError:
  print("错误: json.load 需要文件对象，而不是文件路径！")

# 预加载 YOLO 模型（确保模型文件路径正确）
model = YOLO(MODEL_PATH)


@router.post("/image2hmi")
async def image2hmi(file: UploadFile = File(..., description="上传的文件")):
  # 检查 MIME 类型
  if file.content_type.lower() not in ALLOWED_MIME_TYPES:
    raise HTTPException(400, "仅支持 JPG/PNG 格式图片")

    # 检查文件扩展名（双重验证）
  file_extension = re.split(r"\.", file.filename)[-1].lower()
  if file_extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(400, "文件扩展名无效")

  fileInfo = {
    "filename": file.filename,
    "content_type": file.content_type,
    "size": file.size,
  }
  # --------------- 读取文件内容 ---------------
  try:
    # 读取文件内容
    content = await file.read()
  except Exception as e:
    raise HTTPException(500, f"文件读取失败: {str(e)}")

  # --------------- 将字节数据转换为 OpenCV 格式 ---------------
  try:
    # 将字节流转换为 numpy 数组
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # BGR 格式
    if img is None:
      raise ValueError("无法解码图片")
  except Exception as e:
    raise HTTPException(400, f"图像解码失败: {str(e)}")

  # --------------- 使用 YOLO 模型检测 ---------------
  try:
    results = model.predict(source=img, verbose=False)  # 直接传入 numpy 数组
  except Exception as e:
    raise HTTPException(500, f"模型推理失败: {str(e)}")

  # 返回事件流响应
  return StreamingResponse(
    events_generator(results, fileInfo), media_type="text/event-stream"
  )


async def events_generator(list: List[Results], fileInfo: dict):
  """
  事件生成器函数
  """
  yield "event: start\ndata: 开始图片分析任务\n\n"
  # 假装在思考
  msg = f"收到用户发送的图片{
    fileInfo['filename']
  }, 我需要识别这个图片中的内容, 转换为 HMI 符号, 并在当前图纸上绘制出来."

  yield f"event: message\ndata: {msg}\n\n"
  await asyncio.sleep(0.2)
  yield "event: message\ndata: 开始绘制:\n\n"
  index = 0
  for item in list:
    for box in item.boxes:
      await asyncio.sleep(0.2)
      cls = box.cls.item()
      cls_name = item.names[int(cls)]
      payload = convert_name_to_hmi_symbol(cls_name)
      if payload is None:
        continue
      # x1, y1, x2, y2 分别是目标检测框（bounding box）的左上角和右下角的坐标
      x1, y1, x2, y2 = box.xyxy[0].tolist()
      attrs = calculate_area(x1, y1, x2, y2)
      conf = box.conf.item()
      index += 1
      yield f"event: message\ndata: {index}. {cls_name} <br />\n\n"
      await asyncio.sleep(0.2)
      # 转换为 JSON 可序列化格式
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

  # 这里可以添加更多的处理逻辑，例如保存结果、绘制框等
  yield "event: done\ndata: 图片分析任务完成\n\n"


def convert_name_to_hmi_symbol(name: str):
  """
  将名称转换为 HMI 符号,未找到时返回 None
  """
  flag = SYMBOL_NAME_MAPPING.get(name, None)
  if flag is None:
    print(f"未找到名称: {name}")
  return flag


def calculate_area(x1: float, y1: float, x2: float, y2: float):
  """
  计算图符位置和大小
  parameters:
    x1 (float): 左上角 x 坐标
    y1 (float): 左上角 y 坐标
    x2 (float): 右下角 x 坐标
    y2 (float): 右下角 y 坐标
  returns:
    dict: 包含 x(int), y(int), width(int), height(int) 的字典
  """
  return {
    "x": int(x1),
    "y": int(y1),
    "width": abs(int(x2) - int(x1)),
    "height": abs(int(y2) - int(y1)),
  }
