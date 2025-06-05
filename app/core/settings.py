"""配置/环境相关的处理"""

import os
from pathlib import Path


class Settings:
  """应用程序设置"""

  _instance = None

  def __new__(cls, *args, **kwargs):
    if not hasattr(cls, "_instance") or cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self):
    if hasattr(self, "_initialized") and self._initialized:
      return
    self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")
    self.MODEL = os.getenv("MODEL", "deepseek-chat")
    self.TEMPERATURE = float(os.getenv("TEMPERATURE", 1.0))
    self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    self.TOP_P = float(os.getenv("TOP_P", 1.0))

    # 服务器发送事件(SSE)的间隔时间,单位为秒
    self.SERVER_SEND_EVENTS_INTERVAL = float(
      os.getenv("SERVER_SEND_EVENTS_INTERVAL", 0.1)
    )  # 秒
    """服务器发送事件(SSE)的间隔时间,单位为秒"""

    self.MODEL_PATH = (
      Path(__file__).parent.parent.parent / "models/hollysys-hmi.pt"
    )
    """YOLO图符识别模型文件路径"""

    self.MODEL_LINE_PATH = (
      Path(__file__).parent.parent.parent / "models/hollysys-hmi-line.pt"
    )
    """YOLO线条/管道识别模型文件路径"""

    self.SYMBOL_MAPPING_PATH = (
      Path(__file__).parent.parent.parent / "hmi-symbol-mapping.json"
    )
    """HMI符号映射文件路径"""


settings = Settings()
"""应用程序设置实例"""
