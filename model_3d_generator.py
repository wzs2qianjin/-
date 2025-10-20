# 模块文件名:model_3d_generator.py
from hull_interface import HullBasicParams, Hull2DLineData, Hull3DWireframeData
import numpy as np
from typing import List, Tuple, Protocol
import logging


# 设置日志
logger = logging.getLogger(__name__)

class InterpolationFunction(Protocol):
    """插值函数协议"""
    def __call__(self, x: float) -> float: ...
    
def _validate_input_data(two_d_data: Hull2DLineData) -> None:
    """验证输入数据的完整性"""
    if not two_d_data.side_profile:
        raise ValueError("侧面轮廓数据为空")
    
    if not two_d_data.half_breadth:
        raise ValueError("半宽图数据为空")
    
    if len(two_d_data.side_profile) < 2:
        raise ValueError("侧面轮廓数据点太少,至少需要2个点")
    
    # 检查侧面轮廓x坐标是否单调递增
    side_x = [p[0] for p in two_d_data.side_profile]
    if not all(side_x[i] <= side_x[i+1] for i in range(len(side_x)-1)):
        raise ValueError("侧面轮廓x坐标必须单调递增")
    
    # 检查半宽图x坐标范围
    half_x = [p[0] for p in two_d_data.half_breadth]
    if half_x:
        side_x_min, side_x_max = min(side_x), max(side_x)
        half_x_min, half_x_max = min(half_x), max(half_x)
        
        if half_x_max < side_x_min or half_x_min > side_x_max:
            logger.warning("半宽图x坐标范围与侧面轮廓不匹配,可能产生外推结果")

def _create_interpolation_function(half_breadth: List[Tuple[float, float]]) -> InterpolationFunction:
    """创建半宽图插值函数"""
    if not half_breadth:
        raise ValueError("半宽图数据为空")
    
    # 按x坐标排序
    half_breadth_sorted = sorted(half_breadth, key=lambda point: point[0])
    x_half = [point[0] for point in half_breadth_sorted]
    y_half = [point[1] for point in half_breadth_sorted]
    
    # 处理不同的数据点情况
    if len(x_half) == 1:
        # 单点情况：常数插值
        constant_y = y_half[0]
        logger.debug("使用常数插值,y = %f", constant_y)
        return lambda x: constant_y
    
    elif len(x_half) == 2:
        # 两点情况：线性插值
        x1, y1 = x_half[0], y_half[0]
        x2, y2 = x_half[1], y_half[1]
        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
        
        def linear_interp(x: float) -> float:
            if x <= x1:
                return y1
            elif x >= x2:
                return y2
            else:
                return y1 + slope * (x - x1)
        
        logger.debug("使用两点线性插值")
        return linear_interp
    
    else:
        # 多点情况：使用numpy插值（自动处理外推）
        logger.debug("使用numpy线性插值,数据点: %d", len(x_half))
        return lambda x: float(np.interp(x, x_half, y_half))

def generate_3d_wireframe(params: HullBasicParams, two_d_data: Hull2DLineData) -> Hull3DWireframeData:
    """
    功能: 根据2D型线数据生成3D线框模型(使用NumPy插值优化)
    输入:
        - params(子模块2的合格参数): HullBasicParams对象,包含基本设计参数
        - two_d_data(子模块3的2D型线数据,参数名改为有效名称): Hull2DLineData对象,包含2D型线数据(侧面轮廓和半宽图)
    输出: Hull3DWireframeData对象(3D线框数据)
    算法:
        1. 顶点生成:
            - 对半宽图数据排序,使用np.interp为每个侧面轮廓点(x,z)插值得到y值
            - 生成对称顶点(x,y,z)和(x,-y,z)
        2. 边生成:
            - 连接同一x位置的对称顶点
            - 连接相邻x位置的顶点形成纵向边
    """
    logger.info("开始生成3D线框模型,版本: %d", two_d_data.line_version)
    
    # 1. 输入验证
    _validate_input_data(two_d_data)
    
    # 2. 创建插值函数
    interpolate_y = _create_interpolation_function(two_d_data.half_breadth)
    
    vertices: List[Tuple[float, float, float]] = []
    edges: List[Tuple[int, int]] = []

    # 从侧面轮廓和半宽图生成顶点
    for i, (x_side, z_side) in enumerate(two_d_data.side_profile):
        try:
            # 插值得到y值
            y_val = interpolate_y(x_side)
            
            # 确保y值非负
            if y_val < 0:
                logger.warning("x=%.2f处的半宽为负值,已自动取绝对值", x_side)
                y_val = abs(y_val)
        
            # 生成对称顶点(y和-y)
            vertices.append((x_side, y_val, z_side))
            vertices.append((x_side, -y_val, z_side))

            # 生成边:连接同一x位置的对称顶点(顶点索引为2*i和2*i+1)
            edges.append((2 * i, 2 * i + 1))

        except Exception as e:
            logger.error("在处理侧面轮廓点(%f, %f)时出错: %s", x_side, z_side, e)
            raise
    
    # 生成纵向边:连接相邻x位置的顶点
    n_points = len(two_d_data.side_profile)
    if n_points >= 2:
        for i in range(n_points - 1):
            # 右舷纵向边
            edges.append((2 * i, 2 * (i + 1)))
            # 左舷纵向边  
            edges.append((2 * i + 1, 2 * (i + 1) + 1))
    
    logger.info("3D线框生成完成: %d个顶点, %d条边", len(vertices), len(edges))
    
    return Hull3DWireframeData(
        vertices = vertices,
        edges = edges,
        model_version = two_d_data.line_version  # 使用2D数据的版本
    )