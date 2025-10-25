# hull_interface.py
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ------------------------------
# 1. 船体基本参数数据结构(子模块1→2→3/5传递)
# ------------------------------
@dataclass
class HullBasicParams:
    """
    存储用户输入的船体基本参数(单位:米m)
    说明:参数名与文档一致,避免歧义
    """
    Lpp: float  # 垂线间长(优先用Lpp,无则用Loa)
    B: float  # 船宽
    D: float    # 型深
    T: float    # 吃水
    Delta: float  # 排水量(单位:吨t)
    Loa: Optional[float] = None  # 总长(可选,若用户没输则为None)
    param_source: str = "user_input"  # 参数来源(默认用户输入,后续可扩展为“文件导入”)

# ------------------------------
# 2. 2D型线数据结构(子模块3→4/6传递)
# ------------------------------
@dataclass
class Hull2DLineData:
    """
    存储2D型线的坐标数据(所有坐标单位:米m,以船中为原点,x轴向前,y轴向右,z轴向上)
    说明:每个型线用“点列表”存储(如side_profile是[(x1,z1), (x2,z2), ...]),方便绘图和调整
    """
    # 侧面轮廓线(x: 纵向位置,z: 高度)
    side_profile: List[Tuple[float, float]]
    # 半宽图线(x: 纵向位置,y: 半宽)
    half_breadth: List[Tuple[float, float]]
    # 横剖面图线(多个横剖面,key是x坐标,value是该位置的(y,z)点列表)
    cross_sections: dict[float, List[Tuple[float, float]]]
    line_version: int = 1  # 型线版本号(每次修改+1,避免数据混乱)

# ------------------------------
# 3. 3D线框模型数据结构(子模块5→6传递)
# ------------------------------
@dataclass
class Hull3DWireframeData:
    """
    存储3D线框模型数据(顶点+边,方便PyVista/Matplotlib渲染)
    """
    # 顶点列表:[(x1,y1,z1), (x2,y2,z2), ...]
    vertices: List[Tuple[float, float, float]]
    # 边列表:每个边是两个顶点的索引(如(0,1)表示连接顶点0和顶点1)
    edges: List[Tuple[int, int]]
    model_version: int = 1  # 模型版本号(与2D型线版本号对应)

# ------------------------------
# 4. 交互事件数据结构(子模块4→3/6传递)
# ------------------------------
@dataclass
class InteractionEvent:
    """
    存储用户交互式调整的事件信息(子模块4捕获后,传递给其他模块触发更新)
    """
    event_type: str  # 事件类型:"drag_start"(拖拽开始)、"dragging"(拖拽中)、"drag_end"(拖拽结束)
    line_type: str   # 被修改的型线类型:"side_profile"(侧面轮廓)、"half_breadth"(半宽)、"cross_section"(横剖面)
    target_point_idx: int  # 被拖拽的点在“点列表”中的索引(如side_profile的第5个点)
    new_coords: Tuple[float, float]  # 拖拽后的新坐标(2D坐标,如(x,z)或(x,y))
    cross_section_x: Optional[float] = None  # 若修改横剖面,需指定横剖面的x坐标(其他型线为None)

# ------------------------------
# 5. 参数校验结果数据结构(子模块2→1/3传递)
# ------------------------------
@dataclass
class ParamCheckResult:
    """
    存储参数校验的结果(子模块2返回给子模块1,用于显示错误提示)
    """
    is_valid: bool  # 是否合格(True=合格,False=不合格)
    error_msg: str  # 错误信息(合格则为"",不合格则说明原因,如“船长必须大于船宽”)
    valid_params: Optional[HullBasicParams] = None  # 合格的参数(不合格则为None)