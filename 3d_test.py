# 3d_test.py
"""
3D线框模型可视化
生成详细的船舶3D线框模型并可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from core.hull_interface import HullBasicParams, Hull2DLineData
from model_3d_generator import generate_3d_wireframe

def create_detailed_2d_data():
    """创建详细的2D型线数据（更多点）"""
    print("创建详细的2D型线数据...")
    
    # 侧面轮廓线 - 更多点
    side_profile = []
    for i in range(21):  # 21个点
        x = i * 0.6  # 从0到12米
        if x <= 3.0:
            z = 0.5 * x  # 船尾线性上升
        elif x <= 9.0:
            z = 1.5 + 0.5 * np.sin((x-3.0)*np.pi/6)  # 船中弧形
        else:
            z = 1.5 - 0.5 * (x-9.0)  # 船首线性下降
        side_profile.append((x, z))
    
    # 半宽图 - 更多点
    half_breadth = []
    for i in range(21):
        x = i * 0.6
        if x <= 3.0:
            y = 0.3 + 0.7 * (x/3.0)  # 船尾宽度增加
        elif x <= 9.0:
            y = 1.0 + 1.0 * np.sin((x-3.0)*np.pi/6)  # 船中最大宽度
        else:
            y = 1.0 - 0.7 * (x-9.0)/3.0  # 船首宽度减小
        half_breadth.append((x, y))
    
    # 横剖面 - 更多点
    cross_sections = {}
    for x_pos in [3.0, 6.0, 9.0]:
        points = []
        for angle in np.linspace(0, 2*np.pi, 20):  # 20个点形成圆形截面
            radius = 1.0 + 0.5 * np.sin(angle*2)  # 椭圆形截面
            y = radius * np.cos(angle)
            z = radius * np.sin(angle) + 1.5  # 中心上移
            points.append((y, z))
        cross_sections[x_pos] = points
    
    hull_2d = Hull2DLineData(side_profile, half_breadth, cross_sections)
    print(f"侧面轮廓: {len(side_profile)}个点")
    print(f"半宽图: {len(half_breadth)}个点")
    print(f"横剖面: {len(cross_sections)}个截面")
    
    return hull_2d

def create_ship_params():
    """创建船舶参数"""
    return HullBasicParams(
        Lpp=12.0,    # 垂线间长 12米
        B=4.0,       # 船宽 4米
        D=3.0,       # 型深 3米
        T=2.5,       # 吃水 2.5米
        Delta=100.0  # 排水量 100吨
    )

def visualize_wireframe(hull_3d):
    """可视化3D线框模型"""
    print("生成3D可视化...")
    
    # 创建图形
    fig = plt.figure(figsize=(15, 10))
    
    # 3D视图
    ax1 = fig.add_subplot(221, projection='3d')
    ax2 = fig.add_subplot(222, projection='3d')
    ax3 = fig.add_subplot(223, projection='3d')
    ax4 = fig.add_subplot(224, projection='3d')
    
    # 提取顶点和边
    vertices = np.array(hull_3d.vertices)
    edges = hull_3d.edges
    
    # 绘制所有视图
    views = [
        (ax1, "等轴视图", (30, 45)),
        (ax2, "侧视图", (0, 0)),
        (ax3, "俯视图", (90, 0)),
        (ax4, "前视图", (0, 90))
    ]
    
    for ax, title, elev_azim in views:
        # 设置视角
        ax.view_init(elev=elev_azim[0], azim=elev_azim[1])
        
        # 绘制边
        for edge in edges:
            v1, v2 = vertices[edge[0]], vertices[edge[1]]
            ax.plot([v1[0], v2[0]], [v1[1], v2[1]], [v1[2], v2[2]], 
                   'b-', linewidth=0.8, alpha=0.7)
        
        # 绘制顶点
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                  c='r', s=10, alpha=0.5)
        
        # 设置标签和标题
        ax.set_xlabel('X (长度)')
        ax.set_ylabel('Y (宽度)')
        ax.set_zlabel('Z (高度)')
        ax.set_title(title)
        
        # 设置相等的比例尺
        max_range = max(vertices[:, 0].max()-vertices[:, 0].min(),
                       vertices[:, 1].max()-vertices[:, 1].min(),
                       vertices[:, 2].max()-vertices[:, 2].min())
        mid_x = (vertices[:, 0].max()+vertices[:, 0].min()) * 0.5
        mid_y = (vertices[:, 1].max()+vertices[:, 1].min()) * 0.5
        mid_z = (vertices[:, 2].max()+vertices[:, 2].min()) * 0.5
        ax.set_xlim(mid_x - max_range*0.5, mid_x + max_range*0.5)
        ax.set_ylim(mid_y - max_range*0.5, mid_y + max_range*0.5)
        ax.set_zlim(mid_z - max_range*0.5, mid_z + max_range*0.5)
    
    plt.tight_layout()
    plt.show()
    
    # 打印模型信息
    print(f"\n3D模型信息:")
    print(f"顶点数量: {len(vertices)}")
    print(f"边数量: {len(edges)}")
    print(f"模型尺寸: {vertices[:, 0].max()-vertices[:, 0].min():.2f} × "
          f"{vertices[:, 1].max()-vertices[:, 1].min():.2f} × "
          f"{vertices[:, 2].max()-vertices[:, 2].min():.2f} 米")

def create_high_density_model():
    """创建高密度模型（更多点）"""
    print("创建高密度3D模型...")
    
    # 侧面轮廓线 - 非常高密度
    side_profile = []
    for i in range(51):  # 51个点
        x = i * 12.0 / 50  # 从0到12米
        # 更复杂的船体形状
        if x <= 2.0:
            z = 0.2 * x  # 船尾
        elif x <= 4.0:
            z = 0.4 + 0.3 * (x-2.0)  # 过渡区
        elif x <= 8.0:
            z = 1.0 + 0.5 * np.sin((x-4.0)*np.pi/4)  # 船中
        elif x <= 10.0:
            z = 1.5 - 0.3 * (x-8.0)  # 过渡区
        else:
            z = 0.9 - 0.9 * (x-10.0)/2.0  # 船首
        side_profile.append((x, z))
    
    # 半宽图 - 非常高密度
    half_breadth = []
    for i in range(51):
        x = i * 12.0 / 50
        # 更复杂的宽度分布
        if x <= 2.0:
            y = 0.2 + 0.8 * (x/2.0)  # 船尾
        elif x <= 5.0:
            y = 1.0 + 0.5 * (x-2.0)/3.0  # 增加
        elif x <= 7.0:
            y = 1.5 + 0.3 * np.sin((x-5.0)*np.pi/2)  # 船中
        elif x <= 10.0:
            y = 1.5 - 0.5 * (x-7.0)/3.0  # 减小
        else:
            y = 1.0 - 0.8 * (x-10.0)/2.0  # 船首
        half_breadth.append((x, y))
    
    hull_2d = Hull2DLineData(side_profile, half_breadth, {})
    params = HullBasicParams(Lpp=12.0, B=4.0, D=3.0, T=2.5, Delta=100.0)
    
    hull_3d = generate_3d_wireframe(params, hull_2d)
    print(f"高密度模型: {len(hull_3d.vertices)}个顶点, {len(hull_3d.edges)}条边")
    
    return hull_3d

def main():
    """主函数"""
    print("🚢 3D线框模型可视化")
    print("=" * 50)
    
    try:
        # 选择模型密度
        print("选择模型密度:")
        print("1. 标准密度 (~100个顶点)")
        print("2. 高密度 (~500个顶点)")
        
        choice = input("请输入选择 (1或2, 默认1): ").strip()
        
        if choice == "2":
            hull_3d = create_high_density_model()
        else:
            # 创建标准模型
            params = create_ship_params()
            hull_2d = create_detailed_2d_data()
            hull_3d = generate_3d_wireframe(params, hull_2d)
        
        # 可视化
        visualize_wireframe(hull_3d)
        
        print("\n✅ 3D可视化完成!")
        
    except Exception as e:
        print(f"❌ 可视化过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()