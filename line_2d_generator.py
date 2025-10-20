# 模块文件名：line_2d_generator.py
from hull_interface import HullBasicParams, Hull2DLineData, InteractionEvent
import numpy as np


def generate_initial_2d_lines(params: HullBasicParams) -> Hull2DLineData:
    """
    功能：根据合格参数生成初始2D型线（简化算法，适合本科生实现）
    输入：params（子模块2提供的合格参数）
    输出：Hull2DLineData对象（初始2D型线数据）
    简化算法建议（避免复杂船舶型线公式）：
    1. 侧面轮廓（side_profile）：
       - 纵向x范围：-Lpp/2 ~ Lpp/2（船中为原点，向前为正）
       - 高度z范围：0 ~ D（吃水T以下为水下，T以上为水上）
       - 船首/船尾用简单抛物线：x=-Lpp/2时z=0（船尾底），x=-Lpp/2+10时z=T（船尾水线）
    2. 半宽图（half_breadth）：
       - 纵向x范围：-Lpp/2 ~ Lpp/2
       - 半宽y范围：0 ~ B/2（船中x=0时y最大为B/2，船首/船尾逐渐减到0）
    3. 横剖面图（cross_sections）：
       - 选取3个关键截面：x=-Lpp/4（船尾）、x=0（船中）、x=Lpp/4（船首）
       - 船中截面（x=0）：y范围-B/2~B/2，z范围0~D，水下（z≤T）为矩形，水上（z>T）为梯形
    """
    # 示例：生成侧面轮廓（简化）
    x_side = np.linspace(-params.Lpp / 2, params.Lpp / 2, 50)  # 50个点，避免太稀疏
    z_side = np.where(
        x_side < -params.Lpp / 2 + 5,  # 船尾5米内，z从0升到T
        (params.T / 5) * (x_side + params.Lpp / 2),
        np.where(
            x_side > params.Lpp / 2 - 5,  # 船首5米内，z从T降到0
            params.T - (params.T / 5) * (x_side - (params.Lpp / 2 - 5)),
            params.T  # 中间段，z=T（水线高度）
        )
    )
    side_profile = list(zip(x_side.tolist(), z_side.tolist()))

    # 其他型线（半宽图、横剖面图）按类似简化逻辑实现...
    half_breadth = []  # 开发者补充
    cross_sections = {}  # 开发者补充

    return Hull2DLineData(
        side_profile=side_profile,
        half_breadth=half_breadth,
        cross_sections=cross_sections,
        line_version=1
    )


def update_2d_lines(old_2d_data: Hull2DLineData, event: InteractionEvent) -> Hull2DLineData:
    """
    功能：根据用户交互事件（拖拽）更新2D型线数据
    输入：
        - old_2d_data（当前的2D型线数据）
        - event（子模块4传递的交互事件）
    输出：更新后的Hull2DLineData对象（version+1）
    逻辑示例：
    - 若event.line_type是"side_profile"，则修改old_2d_data.side_profile[event.target_point_idx]为event.new_coords
    """
    # 复制旧数据，避免修改原对象
    new_side = old_2d_data.side_profile.copy()
    new_half = old_2d_data.half_breadth.copy()
    new_cross = old_2d_data.cross_sections.copy()

    if event.line_type == "side_profile":
        new_side[event.target_point_idx] = event.new_coords
    elif event.line_type == "half_breadth":
        new_half[event.target_point_idx] = event.new_coords
    elif event.line_type == "cross_section" and event.cross_section_x is not None:
        new_cross[event.cross_section_x][event.target_point_idx] = event.new_coords

    return Hull2DLineData(
        side_profile=new_side,
        half_breadth=new_half,
        cross_sections=new_cross,
        line_version=old_2d_data.line_version + 1
    )