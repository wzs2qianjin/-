# 模块文件名：model_renderer.py
from hull_interface import Hull2DLineData, Hull3DWireframeData, InteractionEvent
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyvista as pv
from PyQt5.QtWidgets import QTabWidget, QWidget


def create_render_window() -> QTabWidget:
    """
    功能：创建渲染窗口（分2个标签页：2D型线图、3D线框模型）
    输入：无
    输出：QTabWidget（包含2个标签页的窗口）
    """
    tab_widget = QTabWidget()

    # 2D标签页（用Matplotlib）
    self.fig_2d, (ax_side, ax_half, ax_cross) = plt.subplots(1, 3, figsize=(15, 5))
    self.canvas_2d = FigureCanvas(self.fig_2d)
    tab_2d = QWidget()
    tab_2d.layout().addWidget(self.canvas_2d)
    tab_widget.addTab(tab_2d, "2D型线图")

    # 3D标签页（用PyVista）
    self.pv_plotter = pv.Plotter(window_size=[800, 600])
    self.canvas_3d = self.pv_plotter.show(interactive=False, embed=True)
    tab_3d = QWidget()
    tab_3d.layout().addWidget(self.canvas_3d)
    tab_widget.addTab(tab_3d, "3D线框模型")

    return tab_widget


def render_2d_lines(canvas_2d: FigureCanvas, 2d_data: Hull2DLineData) -> None:
    """
    功能：在2D标签页渲染型线图
    输入：
        - canvas_2d（2D绘图画布）
        - 2d_data（子模块3的2D型线数据）
    输出：无（画布刷新显示）
    逻辑：
    1. 清空之前的绘图
    2. 在ax_side画side_profile，ax_half画half_breadth，ax_cross画cross_sections
    3. 绘制控制点（红色小圆点）
    4. 调用canvas_2d.draw()刷新
    """
    pass


def render_3d_model(pv_plotter: pv.Plotter, 3d_data: Hull3DWireframeData) -> None:
    """
    功能：在3D标签页渲染线框模型
    输入：
        - pv_plotter（PyVista的绘图器）
        - 3d_data（子模块5的3D线框数据）
    输出：无（3D窗口刷新显示）
    逻辑：
    1. 清除之前的模型（pv_plotter.clear()）
    2. 用pv.PolyData创建线框模型（输入vertices和edges）
    3. 用pv_plotter.add_mesh()添加模型，设置颜色为蓝色
    4. 调用pv_plotter.render()刷新
    """
    pass


def update_render_on_interaction(
        canvas_2d: FigureCanvas,
        pv_plotter: pv.Plotter,
        new_2d_data: Hull2DLineData,
        new_3d_data: Hull3DWireframeData
) -> None:
    """
    功能：用户交互调整后，实时更新渲染
    输入：
        - canvas_2d（2D画布）
        - pv_plotter（3D绘图器）
        - new_2d_data（更新后的2D数据）
        - new_3d_data（更新后的3D数据）
    输出：无（调用render_2d_lines和render_3d_model刷新）
    """
    render_2d_lines(canvas_2d, new_2d_data)
    render_3d_model(pv_plotter, new_3d_data)