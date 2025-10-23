# 模块4文件名:multi_segment_ship_editor_interface.py
"""
多段式船体型线编辑器,兼容hull_interface接口
接收来自Hull2DLineData的三种类型型线,支持交互式调整
"""

# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportGeneralTypeIssues=false

from hull_interface import Hull2DLineData, InteractionEvent
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.interpolate import CubicSpline
from typing import List, Tuple, Optional, Dict, Any, Union
import numbers

class MultiSegmentShipEditorInterface:
    """
    多段式船体型线编辑器,兼容hull_interface接口
    支持三种类型型线的交互式调整：
    - 侧面轮廓线 (Side Profile)
    - 半宽图 (Half-Breadth)  
    - 横剖面 (Cross Sections)
    """
    
    def __init__(self, hull_2d_data: Hull2DLineData):
        # 存储提供的2D船体数据
        self.hull_2d_data = hull_2d_data
        
        # 创建图形窗口和子图
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.ax_side = self.axes[0, 0]    # 侧面轮廓图
        self.ax_half = self.axes[0, 1]    # 半宽图
        self.ax_cross = self.axes[1, 0]   # 横剖面图
        self.ax_info = self.axes[1, 1]    # 信息显示面板
        
        # 状态变量
        self.dragging = False              # 是否正在拖拽控制点
        self.dragged_idx = None            # 当前拖拽的控制点索引
        self.dragged_line_type = None      # 当前拖拽的线类型：'side_profile', 'half_breadth', 'cross_section'
        self.dragged_cross_section_x = None  # 当前拖拽的横剖面x坐标
        
        # 控制点集合（存储图形对象）
        self.control_circles = {
            'side_profile': [],    # 侧面轮廓线控制点
            'half_breadth': [],    # 半宽图控制点
            'cross_section': []    # 横剖面控制点
        }
        
        # 曲线集合（存储图形对象）
        self.curve_lines = {
            'side_profile': [],    # 侧面轮廓线
            'half_breadth': [],    # 半宽图曲线
            'cross_section': []    # 横剖面曲线
        }
        
        # 当前选中的横剖面
        self.current_cross_section_x = None
        
        # 坐标轴显示范围限制
        self.side_x_limits: Tuple[float, float] = (-1, 13)    # 侧面图X轴范围
        self.side_y_limits: Tuple[float, float] = (-0.5, 4)   # 侧面图Y轴范围
        self.half_x_limits: Tuple[float, float] = (-1, 13)    # 半宽图X轴范围
        self.half_y_limits: Tuple[float, float] = (-0.5, 3)   # 半宽图Y轴范围
        self.cross_x_limits: Tuple[float, float] = (-3, 3)    # 横剖面图X轴范围
        self.cross_y_limits: Tuple[float, float] = (-0.5, 4)  # 横剖面图Y轴范围
        
        # 控制点样式设置 - 使用统一的控制点半径
        self.control_point_radius = 0.06   # 控制点显示半径
        self.curve_colors: Dict[str, str] = {
            'side_profile': 'black',    # 黑色 - 侧面轮廓线
            'half_breadth': 'black',    # 黑色 - 半宽图
            'cross_section': 'black'    # 黑色 - 横剖面
        }
        
        # 交互事件记录
        self.interaction_events: List[InteractionEvent] = []
        
        print("Multi-segment Ship Lines Editor initialized")
        print(f"Side profile points: {len(hull_2d_data.side_profile)}")
        print(f"Half-breadth points: {len(hull_2d_data.half_breadth)}")
        print(f"Cross sections: {len(hull_2d_data.cross_sections)}")
        
        # 初始化曲线数据并绘制
        self.initialize_curves()
        self.draw_all_curves()
        
        # 绑定交互事件
        self.connect_events()
        
        # 设置图形属性
        self.setup_plots()
    
    def initialize_curves(self) -> None:
        """初始化曲线数据"""
        # 如果数据为空,创建默认数据
        if not self.hull_2d_data.side_profile:
            # 默认侧面轮廓线控制点（船体侧面形状）
            self.hull_2d_data.side_profile = [
                (0.0, 0.0), (1.5, 1.0), (3.0, 1.8),    # 船首部分
                (4.0, 2.2), (6.0, 2.5), (8.0, 2.2),    # 船中部分
                (9.0, 1.8), (10.5, 1.0), (12.0, 0.0)   # 船尾部分
            ]
        
        if not self.hull_2d_data.half_breadth:
            # 默认半宽图控制点（船体宽度分布）
            self.hull_2d_data.half_breadth = [
                (0.0, 0.5), (2.0, 1.0), (4.0, 1.8),    # 船首宽度变化
                (6.0, 2.2), (8.0, 2.0), (10.0, 1.5),   # 船中宽度变化
                (12.0, 0.8)                             # 船尾宽度
            ]
        
        if not self.hull_2d_data.cross_sections:
            # 创建示例横剖面数据（不同位置的船体横截面形状）
            self.hull_2d_data.cross_sections = {
                # x=3.0位置的横剖面（船首附近）
                3.0: [(0.0, 0.0), (1.0, 0.8), (1.5, 1.5), (1.0, 2.2), (0.0, 2.5), 
                      (-1.0, 2.2), (-1.5, 1.5), (-1.0, 0.8), (0.0, 0.0)],
                # x=6.0位置的横剖面（船中位置）
                6.0: [(0.0, 0.0), (1.5, 0.6), (2.0, 1.8), (1.5, 2.8), (0.0, 3.0),
                      (-1.5, 2.8), (-2.0, 1.8), (-1.5, 0.6), (0.0, 0.0)],
                # x=9.0位置的横剖面（船尾附近）
                9.0: [(0.0, 0.0), (1.2, 0.4), (1.8, 1.2), (1.2, 2.0), (0.0, 2.2),
                      (-1.2, 2.0), (-1.8, 1.2), (-1.2, 0.4), (0.0, 0.0)]
            }
        
        # 设置当前显示的横剖面（默认显示第一个）
        if self.hull_2d_data.cross_sections:
            self.current_cross_section_x = list(self.hull_2d_data.cross_sections.keys())[0]
    
    def generate_smooth_curve(self, points: List[Tuple[float, float]], is_closed: bool = False) -> List[Tuple[float, float]]:
        """生成平滑曲线"""
        if len(points) < 2:
            return points
        
        # 根据曲线是否闭合选择不同的插值方法
        if is_closed:
            return self._generate_closed_curve(points)
        else:
            return self._generate_open_curve(points)
    
    def _generate_open_curve(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """生成开放的平滑曲线（用于侧面轮廓线和半宽图）"""
        x_control = [p[0] for p in points]  # 控制点x坐标
        y_control = [p[1] for p in points]  # 控制点y坐标
        
        # 对x坐标进行排序以确保插值稳定性
        sorted_indices = np.argsort(x_control)
        x_sorted = np.array([x_control[i] for i in sorted_indices])
        y_sorted = np.array([y_control[i] for i in sorted_indices])
        
        # 去除重复的x坐标（避免插值错误）
        unique_indices = np.where(np.diff(x_sorted) > 1e-10)[0]
        x_unique = np.concatenate([x_sorted[unique_indices], [x_sorted[-1]]])
        y_unique = np.concatenate([y_sorted[unique_indices], [y_sorted[-1]]])
        
        if len(x_unique) < 2:
            return list(zip(x_sorted.tolist(), y_sorted.tolist()))
        
        try:
            # 使用三次样条插值生成平滑曲线
            cs = CubicSpline(x_unique, y_unique, bc_type='natural')
            # 在控制点范围内生成100个插值点
            x_curve = np.linspace(min(x_unique), max(x_unique), 100)
            y_curve = cs(x_curve)
            
            # 确保使用实数部分（避免复数情况）
            x_curve_real = np.real(x_curve) if np.iscomplexobj(x_curve) else x_curve
            y_curve_real = np.real(y_curve) if np.iscomplexobj(y_curve) else y_curve
            
            # 使用列表推导式将numpy数组转换为Python列表
            return [(float(x), float(y)) for x, y in zip(x_curve_real, y_curve_real)]
        except Exception as e:
            print(f"Open curve interpolation failed, using linear interpolation: {e}")
            return self._linear_interpolation(points)
    
    def _generate_closed_curve(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """生成闭合的平滑曲线（用于横剖面）"""
        if len(points) < 3:
            return points
        
        # 确保曲线闭合（首尾点重合）
        if (abs(points[0][0] - points[-1][0]) > 1e-10 or 
            abs(points[0][1] - points[-1][1]) > 1e-10):
            points = points + [points[0]]  # 添加起始点作为终点以闭合曲线
        
        x_control = [p[0] for p in points]  # 控制点x坐标
        y_control = [p[1] for p in points]  # 控制点y坐标
        
        # 使用参数化样条曲线（适用于闭合曲线）
        t = np.linspace(0, 1, len(x_control))  # 参数化变量
        
        try:
            # 分别对x和y坐标进行周期性样条插值
            cs_x = CubicSpline(t, x_control, bc_type='periodic')
            cs_y = CubicSpline(t, y_control, bc_type='periodic')
            
            # 生成100个插值点
            t_curve = np.linspace(0, 1, 100)
            x_curve = cs_x(t_curve)
            y_curve = cs_y(t_curve)
            
            # 确保使用实数部分
            x_curve_real = np.real(x_curve) if np.iscomplexobj(x_curve) else x_curve
            y_curve_real = np.real(y_curve) if np.iscomplexobj(y_curve) else y_curve
        
            # 将numpy数组转换为Python列表
            return [(float(x), float(y)) for x, y in zip(x_curve_real, y_curve_real)]
        except Exception as e:
            print(f"Closed curve interpolation failed, using linear interpolation: {e}")
            return self._linear_interpolation_closed(points)
    
    def _linear_interpolation(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """线性插值回退方法（当样条插值失败时使用）"""
        if len(points) < 2:
            return points
        
        x_control = [p[0] for p in points]
        y_control = [p[1] for p in points]
        
        # 在控制点范围内生成100个线性插值点
        x_curve = np.linspace(min(x_control), max(x_control), 100)
        y_curve = np.interp(x_curve, x_control, y_control)
        
        return list(zip(x_curve.tolist(), y_curve.tolist()))
    
    def _linear_interpolation_closed(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """闭合曲线线性插值回退方法"""
        if len(points) < 3:
            return points
        
        # 确保曲线闭合
        if (abs(points[0][0] - points[-1][0]) > 1e-10 or 
            abs(points[0][1] - points[-1][1]) > 1e-10):
            points = points + [points[0]]  # 添加起始点作为终点
        
        result: List[Tuple[float, float]] = []
        
        # 在每两个相邻控制点之间进行线性插值
        for i in range(len(points)-1):
            x1, y1 = points[i]      # 当前控制点
            x2, y2 = points[i+1]    # 下一个控制点
            segment_points = 20     # 每段生成20个插值点
            
            for j in range(segment_points):
                t = j / segment_points  # 插值参数
                x = x1 + t * (x2 - x1)  # 线性插值x坐标
                y = y1 + t * (y2 - y1)  # 线性插值y坐标
                result.append((x, y))
        
        return result
    
    def create_circle_patch(self, x: float, y: float, line_type: str) -> Circle:
        """创建控制点圆形标记 - 确保所有控制点使用相同的大小"""
        # 使用统一的控制点半径
        circle = Circle(
            (x, y), self.control_point_radius,  # 圆心位置和半径（统一大小）
            facecolor='red',        # 红色控制点
            edgecolor='white',      # 边框颜色
            linewidth=1.5,          # 边框宽度
            alpha=0.8,              # 透明度
            zorder=5                # 确保控制点显示在曲线上方
        )
        
        # 设置控制点为可选中的（支持鼠标交互）
        try:
            circle.set_picker(True)
        except:
            circle.set_picker(True)
        
        return circle
    
    def draw_all_curves(self):
        """绘制所有曲线和控制点"""
        self.draw_side_profile()    # 绘制侧面轮廓线
        self.draw_half_breadth()    # 绘制半宽图
        self.draw_cross_section()   # 绘制横剖面
        self.update_info_panel()    # 更新信息面板
    
    def draw_side_profile(self) -> None:
        """绘制侧面轮廓线"""
        # 清除之前的图形元素
        for circle in self.control_circles['side_profile']:
            circle.remove()
        self.control_circles['side_profile'].clear()
        
        for line in self.curve_lines['side_profile']:
            line.remove()
        self.curve_lines['side_profile'].clear()
        
        # 生成平滑曲线
        curve_points = self.generate_smooth_curve(self.hull_2d_data.side_profile, False)
        
        # 绘制曲线
        if curve_points:
            x_curve = [p[0] for p in curve_points]  # 曲线点x坐标
            y_curve = [p[1] for p in curve_points]  # 曲线点y坐标
            
            line, = self.ax_side.plot(
                x_curve, y_curve, 
                color=self.curve_colors['side_profile'],  # 黑色曲线
                linewidth=2.5,      # 曲线宽度
                alpha=0.8,          # 透明度
                label='Side Profile'   # 图例标签
            )
            self.curve_lines['side_profile'].append(line)
        
        # 绘制控制点 - 使用统一的方法创建控制点
        for i, (x, y) in enumerate(self.hull_2d_data.side_profile):
            circle = self.create_circle_patch(x, y, 'side_profile')
            self.ax_side.add_patch(circle)  # 将控制点添加到图形中
            self.control_circles['side_profile'].append(circle)
    
    def draw_half_breadth(self) -> None:
        """绘制半宽图"""
        # 清除之前的图形元素
        for circle in self.control_circles['half_breadth']:
            circle.remove()
        self.control_circles['half_breadth'].clear()
        
        for line in self.curve_lines['half_breadth']:
            line.remove()
        self.curve_lines['half_breadth'].clear()
        
        # 生成平滑曲线
        curve_points = self.generate_smooth_curve(self.hull_2d_data.half_breadth, False)
        
        # 绘制曲线
        if curve_points:
            x_curve = [p[0] for p in curve_points]
            y_curve = [p[1] for p in curve_points]
            
            line, = self.ax_half.plot(
                x_curve, y_curve, 
                color=self.curve_colors['half_breadth'],  # 黑色曲线
                linewidth=2.5,
                alpha=0.8,
                label='Half-Breadth'
            )
            self.curve_lines['half_breadth'].append(line)
        
        # 绘制控制点 - 使用统一的方法创建控制点
        for i, (x, y) in enumerate(self.hull_2d_data.half_breadth):
            circle = self.create_circle_patch(x, y, 'half_breadth')
            self.ax_half.add_patch(circle)
            self.control_circles['half_breadth'].append(circle)
    
    def draw_cross_section(self) -> None:
        """绘制横剖面 - 确保控制点大小与其他图一致"""
        # 清除之前的图形元素
        for circle in self.control_circles['cross_section']:
            circle.remove()
        self.control_circles['cross_section'].clear()
        
        for line in self.curve_lines['cross_section']:
            line.remove()
        self.curve_lines['cross_section'].clear()
        
        # 检查当前横剖面是否存在
        if self.current_cross_section_x is None:
            return
        
        # 安全地访问字典数据（包含类型检查）
        cross_section_key = self.current_cross_section_x
        if cross_section_key not in self.hull_2d_data.cross_sections:
            return
        
        # 获取当前横剖面的控制点
        cross_points = self.hull_2d_data.cross_sections.get(self.current_cross_section_x, [])
        if not cross_points:
            return
        
        # 生成平滑的闭合曲线
        curve_points = self.generate_smooth_curve(cross_points, True)
        
        # 绘制曲线
        if curve_points:
            x_curve = [p[0] for p in curve_points]
            y_curve = [p[1] for p in curve_points]
            
            line, = self.ax_cross.plot(
                x_curve, y_curve, 
                color=self.curve_colors['cross_section'],  # 黑色曲线
                linewidth=2.5,
                alpha=0.8,
                label=f'Cross Section (x={self.current_cross_section_x})'  # 显示横剖面位置
            )
            self.curve_lines['cross_section'].append(line)
        
        # 绘制控制点 - 使用与其他图相同的控制点创建方法
        for i, (x, y) in enumerate(cross_points):
            circle = self.create_circle_patch(x, y, 'cross_section')
            self.ax_cross.add_patch(circle)
            self.control_circles['cross_section'].append(circle)
    
    def update_info_panel(self):
        """更新信息显示面板"""
        self.ax_info.clear()  # 清除之前的内容
        
        # 显示基本信息
        info_text = [
            "Ship Lines Editor Information",
            "=" * 30,
            f"Side Profile Points: {len(self.hull_2d_data.side_profile)}",
            f"Half-Breadth Points: {len(self.hull_2d_data.half_breadth)}",
            f"Cross Sections: {len(self.hull_2d_data.cross_sections)}",
            f"Current Cross Section: x={self.current_cross_section_x}",
            f"Data Version: {self.hull_2d_data.line_version}",
            "",
            "Interaction Events:",
            f"Event Count: {len(self.interaction_events)}"
        ]
        
        # 显示最近的交互事件（最后5个）
        recent_events = self.interaction_events[-5:]
        for event in recent_events:
            info_text.append(f"- {event.event_type}: {event.line_type}[{event.target_point_idx}]")
        
        # 添加使用说明
        info_text.extend([
            "",
            "Instructions:",
            "• Drag control points to modify curves",
            "• Three line types can be edited independently",
            "• Interaction events are automatically recorded"
        ])
        
        # 在信息面板中显示文本,调整位置避免重叠
        self.ax_info.text(0.05, 0.95, "\n".join(info_text), 
                         transform=self.ax_info.transAxes,  # 使用相对坐标
                         fontsize=9,                       # 减小字体大小
                         verticalalignment='top',          # 顶部对齐
                         bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8))  # 文本框样式
        
        # 设置信息面板的坐标范围和刻度
        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)
        self.ax_info.set_xticks([])  # 隐藏x轴刻度
        self.ax_info.set_yticks([])  # 隐藏y轴刻度
        self.ax_info.set_title('Information Panel', fontsize=12)
    
    def setup_plots(self):
        """设置图形属性"""
        # 侧面轮廓图设置
        self.ax_side.set_xlabel('Length Direction (m)', fontsize=12)
        self.ax_side.set_ylabel('Depth Direction (m)', fontsize=12)
        self.ax_side.set_title('Side Profile', fontsize=14, fontweight='bold')
        self.ax_side.grid(True, alpha=0.3)  # 显示网格
        self.ax_side.legend(fontsize=10, loc='upper right')    # 显示图例,调整位置
        self.ax_side.set_aspect('equal')    # 设置等比例显示
        self.ax_side.set_xlim(self.side_x_limits[0], self.side_x_limits[1])
        self.ax_side.set_ylim(self.side_y_limits[0], self.side_y_limits[1])
        
        # 半宽图设置
        self.ax_half.set_xlabel('Length Direction (m)', fontsize=12)
        self.ax_half.set_ylabel('Half-Breadth (m)', fontsize=12)
        self.ax_half.set_title('Half-Breadth Diagram', fontsize=14, fontweight='bold')
        self.ax_half.grid(True, alpha=0.3)
        self.ax_half.legend(fontsize=10, loc='upper right')
        self.ax_half.set_aspect('equal')
        self.ax_half.set_xlim(self.half_x_limits[0], self.half_x_limits[1])
        self.ax_half.set_ylim(self.half_y_limits[0], self.half_y_limits[1])
        
        # 横剖面图设置
        self.ax_cross.set_xlabel('Width Direction (m)', fontsize=12)
        self.ax_cross.set_ylabel('Height Direction (m)', fontsize=12)
        self.ax_cross.set_title('Cross Sections', fontsize=14, fontweight='bold')
        self.ax_cross.grid(True, alpha=0.3)
        self.ax_cross.legend(fontsize=10, loc='upper right')
        self.ax_cross.set_aspect('equal')
        self.ax_cross.set_xlim(self.cross_x_limits[0], self.cross_x_limits[1])
        self.ax_cross.set_ylim(self.cross_y_limits[0], self.cross_y_limits[1])
        
        # 信息面板设置
        self.ax_info.set_title('Information Panel', fontsize=12)
        
        # 图形总标题
        self.fig.suptitle('Ship Lines Interactive Editor - hull_interface Compatible', 
                         fontsize=16, fontweight='bold', y=0.98)  # 调整标题位置
        
        # 调整布局,增加子图间距
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为顶部标题留出空间
    
    def connect_events(self) -> None:
        """绑定事件处理函数"""
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)    # 鼠标按下事件
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)    # 鼠标拖拽事件
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)  # 鼠标释放事件
    
    def on_press(self, event) -> None:
        """鼠标按下事件处理"""
        if event.button != 1 or not event.inaxes:  # 只响应左键点击且在坐标轴内
            return
        
        # 检测每种线类型的控制点
        for line_type in ['side_profile', 'half_breadth', 'cross_section']:
            for i, circle in enumerate(self.control_circles[line_type]):
                center = circle.center  # 控制点圆心坐标
                # 计算鼠标位置与控制点的距离
                distance = np.sqrt((event.xdata - center[0])**2 + (event.ydata - center[1])**2)
                
                # 如果距离在控制点半径1.5倍范围内,认为选中了该控制点
                # 所有控制点使用相同的半径,确保选取范围一致
                if distance <= self.control_point_radius * 1.5:
                    self.dragging = True           # 设置拖拽状态
                    self.dragged_idx = i           # 记录拖拽的控制点索引
                    self.dragged_line_type = line_type  # 记录拖拽的线类型
                    
                    # 如果是横剖面,记录当前横剖面的x坐标
                    if line_type == 'cross_section':
                        self.dragged_cross_section_x = self.current_cross_section_x
                    
                    # 高亮显示选中的控制点
                    self.highlight_control_point(i, line_type)
                    
                    # 记录交互事件
                    interaction_event = InteractionEvent(
                        event_type="drag_start",    # 事件类型：拖拽开始
                        line_type=line_type,        # 线类型
                        target_point_idx=i,         # 目标点索引
                        new_coords=(center[0], center[1]),  # 当前坐标
                        cross_section_x=self.dragged_cross_section_x  # 横剖面位置
                    )
                    self.interaction_events.append(interaction_event)
                    
                    print(f"Started dragging {line_type} control point {i}")
                    return  # 找到控制点后立即返回
    
    def on_drag(self, event: Any) -> None:
        """鼠标拖拽事件处理"""
        if not self.dragging or self.dragged_idx is None or not event.inaxes:
            return
        
        if event.xdata is None or event.ydata is None:  # 确保坐标有效
            return
        
        # 确保dragged_line_type是字符串类型
        if self.dragged_line_type is None:
            return
        
        # 使用局部变量确保类型安全
        line_type: str = self.dragged_line_type
        
        # 根据线类型获取新的坐标（限制在坐标轴范围内）
        if self.dragged_line_type == 'side_profile':
            new_x = max(self.side_x_limits[0], min(self.side_x_limits[1], event.xdata))
            new_y = max(self.side_y_limits[0], min(self.side_y_limits[1], event.ydata))
            points = self.hull_2d_data.side_profile
        elif self.dragged_line_type == 'half_breadth':
            new_x = max(self.half_x_limits[0], min(self.half_x_limits[1], event.xdata))
            new_y = max(self.half_y_limits[0], min(self.half_y_limits[1], event.ydata))
            points = self.hull_2d_data.half_breadth
        else:  # cross_section
            new_x = max(self.cross_x_limits[0], min(self.cross_x_limits[1], event.xdata))
            new_y = max(self.cross_y_limits[0], min(self.cross_y_limits[1], event.ydata))
            if self.dragged_cross_section_x is not None:
                points = self.hull_2d_data.cross_sections.get(self.dragged_cross_section_x, [])
            else:
                points = []
        
        # 更新控制点位置
        if self.dragged_idx < len(points):
            points[self.dragged_idx] = (new_x, new_y)
            
            # 更新控制点显示位置
            circle = self.control_circles[line_type][self.dragged_idx]
            circle.center = (new_x, new_y)
            
            # 更新对应的曲线
            self.update_curve_only(line_type)
            
            # 记录拖拽过程中的交互事件
            interaction_event = InteractionEvent(
                event_type="dragging",           # 事件类型：拖拽中
                line_type=self.dragged_line_type,
                target_point_idx=self.dragged_idx,
                new_coords=(new_x, new_y),
                cross_section_x=self.dragged_cross_section_x
            )
            self.interaction_events.append(interaction_event)
    
    def on_release(self, event: Any) -> None:
        """鼠标释放事件处理"""
        if self.dragging and self.dragged_idx is not None and self.dragged_line_type is not None:
            # 确保line_type是字符串类型
            line_type: str = self.dragged_line_type
            
            # 根据线类型获取对应的数据点
            if line_type == 'side_profile':
                points = self.hull_2d_data.side_profile
            elif line_type == 'half_breadth':
                points = self.hull_2d_data.half_breadth
            else:  # cross_section
                if self.dragged_cross_section_x is not None:
                    points = self.hull_2d_data.cross_sections.get(self.dragged_cross_section_x, [])
                else:
                    points = []
            
            # 记录拖拽结束事件
            if self.dragged_idx < len(points):
                interaction_event = InteractionEvent(
                    event_type="drag_end",    # 事件类型：拖拽结束
                    line_type=line_type,
                    target_point_idx=self.dragged_idx,
                    new_coords=points[self.dragged_idx],  # 最终坐标
                    cross_section_x=self.dragged_cross_section_x
                )
                self.interaction_events.append(interaction_event)
                
                # 更新数据版本号（表示数据已被修改）
                self.hull_2d_data.line_version += 1
            
            print(f"Finished dragging {line_type} control point {self.dragged_idx}")
            
            # 更新曲线显示
            self.update_curve_only(line_type)
            
            # 重置控制点颜色（取消高亮）
            self.reset_control_colors()
            
            # 更新信息面板
            self.update_info_panel()
        
        # 重置拖拽状态
        self.dragging = False
        self.dragged_idx = None
        self.dragged_line_type = None
        self.dragged_cross_section_x = None
    
    def highlight_control_point(self, index: int, line_type: str) -> None:
        """高亮显示选中的控制点"""
        for lt in ['side_profile', 'half_breadth', 'cross_section']:
            for i, circle in enumerate(self.control_circles[lt]):
                if lt == line_type and i == index:
                    # 设置选中控制点的样式（黄色高亮）
                    circle.set_facecolor('yellow')       # 填充颜色
                    circle.set_edgecolor('darkorange')   # 边框颜色
                    circle.set_linewidth(2.5)            # 边框宽度
                    circle.set_alpha(1.0)                # 不透明
                else:
                    # 设置其他控制点的默认样式
                    circle.set_facecolor('red')          # 红色控制点
                    circle.set_edgecolor('white')
                    circle.set_linewidth(1.5)
                    circle.set_alpha(0.8)
        
        # 立即更新图形显示
        self.fig.canvas.draw_idle()
    
    def reset_control_colors(self) -> None:
        """重置所有控制点颜色为默认状态"""
        for line_type in ['side_profile', 'half_breadth', 'cross_section']:
            for circle in self.control_circles[line_type]:
                circle.set_facecolor('red')  # 红色控制点
                circle.set_edgecolor('white')
                circle.set_linewidth(1.5)
                circle.set_alpha(0.8)
        
        # 立即更新图形显示
        self.fig.canvas.draw_idle()
    
    def update_curve_only(self, line_type: str) -> None:
        """仅更新指定类型的曲线（优化性能）"""
        if line_type == 'side_profile':
            # 生成新的平滑曲线
            curve_points = self.generate_smooth_curve(self.hull_2d_data.side_profile, False)
            if self.curve_lines['side_profile'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                # 更新曲线数据
                self.curve_lines['side_profile'][0].set_data(x_curve, y_curve)
        
        elif line_type == 'half_breadth':
            curve_points = self.generate_smooth_curve(self.hull_2d_data.half_breadth, False)
            if self.curve_lines['half_breadth'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                self.curve_lines['half_breadth'][0].set_data(x_curve, y_curve)
        
        elif line_type == 'cross_section' and self.current_cross_section_x is not None:
            cross_points = self.hull_2d_data.cross_sections.get(self.current_cross_section_x, [])
            curve_points = self.generate_smooth_curve(cross_points, True)
            if self.curve_lines['cross_section'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                self.curve_lines['cross_section'][0].set_data(x_curve, y_curve)
        
        # 立即更新图形显示
        self.fig.canvas.draw_idle()
    
    def get_interaction_events(self) -> List[InteractionEvent]:
        """获取所有交互事件的副本"""
        return self.interaction_events.copy()
    
    def get_updated_hull_data(self) -> Hull2DLineData:
        """获取更新后的船体数据"""
        return self.hull_2d_data
    
    def show(self) -> None:
        """显示编辑器界面"""
        # 调整布局,增加子图间距
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为顶部标题留出空间
        plt.show()          # 显示图形窗口
