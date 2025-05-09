class SystemFigure:
  """系统图符"""

  # ID

  id: str
  """图符ID"""
  name: str
  """图符名称"""
  description: str
  """图符描述"""

  def __init__(self, id: str, name: str, description: str):
    """
    Args:
      id (str): 图符ID
      name (str): 图符名称
      description (str): 图符描述
    """
    # 初始化图符数据
    self.id = id
    self.name = name
    self.description = description
