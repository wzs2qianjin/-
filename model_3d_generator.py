# 模块文件名：model_3d_generator.py
from hull_interface import HullBasicParams, Hull2DLineData, Hull3DWireframeData
import numpy as np


def generate_3d_wireframe(params: HullBasicParams, 2d_data: Hull2DLineData) -> Hull3DWireframeData:
    """
    功能：根据2D型线数据生成3D线框模型（简化算法，适合本科生）
    输入：
        - params（子模块2的合格参数）
        - 2d_data（子模块3的2D型线数据）
    输出：Hull3DWireframeData对象（3D线框数据）
    简化算法建议：
    1. 顶点生成：
       - 取2D侧面轮廓的每个点（x,z），结合半宽图的对应x位置的y值，生成3D顶点（x,y,z）和（x,-y,z）（对称）
       - 每个横剖面的点（y,z），结合该剖面的x值，生成3D顶点（x,y,z）
    2. 边生成：
       - 连接同一x位置的上下顶点（如(x,0,0)→(x,0,D)）
       - 连接相邻x位置的同一z高度的顶点（如(x1,y,z)→(x2,y,z)）
    """
    vertices = []
    edges = []

    # 示例：从侧面轮廓和半宽图生成顶点
    for i, (x_side, z_side) in enumerate(2d_data.side_profile):
        # 找到半宽图中对应x位置的y值（简化：取x最接近的点的y）
        x_half_list = [x for x, y in 2
        d_data.half_breadth]
        closest_idx = np.argmin(np.abs(np.array(x_half_list) - x_side))
        y_half = 2
        d_data.half_breadth[closest_idx][1]

        # 生成对称顶点（y和-y）
        vertices.append((x_side, y_half, z_side))
        vertices.append((x_side, -y_half, z_side))

        # 生成边：同一x的两个顶点（y和-y）连接
        if i < len(2d_data.side_profile):
            edges.append((2 * i, 2 * i + 1))

    # 其他边（如上下连接、前后连接）按类似逻辑补充...

    return Hull3DWireframeData(
        vertices=vertices,
        edges=edges,
        model_version=2
    d_data.line_version  # 3D模型版本与2D型线版本一致
    )