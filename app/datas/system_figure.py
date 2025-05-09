"""这是存放所有内置图符数据"""

from app.schemas.system_figure import SystemFigure

system_figures_list = [
  SystemFigure(
    id="1",
    name="按钮",
    description="按钮图符",
  ),
  SystemFigure(
    id="2",
    name="开关",
    description="开关图符",
  ),
  SystemFigure(
    id="3",
    name="指示灯",
    description="指示灯图符",
  ),
]
"""系统图符数据"""

system_figures_dict = {figure.id: figure for figure in system_figures_list}
"""系统图符数据字典"""
