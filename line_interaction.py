# 模块文件名：line_interaction.py
from hull_interface import Hull2DLineData, InteractionEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMouseEvent

def bind_interaction_events(plot_widget: QWidget, initial_2d_data: Hull2DLineData) -> None:
    """
    功能：给2D型线绘图窗口绑定鼠标交互事件（拖拽控制点）
    输入：
        - plot_widget（子模块6的2D绘图窗口，如Matplotlib的FigureCanvas）
        - initial_2d_data（子模块3生成的初始2D型线数据）
    输出：无（事件绑定到窗口上）
    核心逻辑：
    1. 绘图时在2D型线的每个点上画“小圆点”（控制点）
    2. 绑定鼠标按压事件（mousePressEvent）：判断是否点击了控制点，记录点击的点索引
    3. 绑定鼠标拖动事件（mouseMoveEvent）：若已点击控制点，更新点坐标，生成InteractionEvent
    4. 绑定鼠标释放事件（mouseReleaseEvent）：结束拖拽，生成“drag_end”事件
    """
    # 开发者需实现：
    # - 用Matplotlib的scatter画控制点（如side_profile的每个点画红色圆点）
    # - 用PyQt的事件绑定函数（如plot_widget.mousePressEvent = on_mouse_press）
    pass

def on_mouse_press(event: QMouseEvent, 2d_data: Hull2DLineData) -> Optional[InteractionEvent]:
    """
    鼠标按压事件处理：判断是否点击控制点，生成“drag_start”事件
    输入：
        - event（鼠标事件，包含点击坐标）
        - 2d_data（当前2D型线数据）
    输出：InteractionEvent（若点击控制点则返回，否则返回None）
    """
    pass

def on_mouse_move(event: QMouseEvent, pressed_point_info: dict) -> Optional[InteractionEvent]:
    """
    鼠标拖动事件处理：生成“dragging”事件
    输入：
        - event（鼠标事件，包含当前坐标）
        - pressed_point_info（按压时记录的点信息：line_type、target_point_idx等）
    输出：InteractionEvent（拖拽中的事件）
    """
    pass

def on_mouse_release(event: QMouseEvent, pressed_point_info: dict) -> Optional[InteractionEvent]:
    """
    鼠标释放事件处理：生成“drag_end”事件
    输入：同on_mouse_move
    输出：InteractionEvent（拖拽结束的事件）
    """
    pass