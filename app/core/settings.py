"""配置/环境相关的处理"""

import os
from pathlib import Path


class Settings:
  """应用程序设置"""

  def __init__(self):
    """初始化设置"""
    self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    self.MODEL = os.getenv("MODEL", "deepseek-chat")
    self.TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    self.TOP_P = float(os.getenv("TOP_P", 1.0))
    self.MODEL_PATH = (
      Path(__file__).parent.parent.parent / "models/hollysys-hmi.pt"
    )
    self.MODEL_LINE_PATH = (
      Path(__file__).parent.parent.parent / "models/hollysys-hmi-line.pt"
    )
    self.SYMBOL_MAPPING_PATH = (
      Path(__file__).parent.parent.parent / "hmi-symbol-mapping.json"
    )


settings = Settings()
"""应用程序设置实例"""
