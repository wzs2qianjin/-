# professional_ship_visualization.py
"""
专业船舶3D线框可视化 - 优化显示效果，确保模型居中
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import RectBivariateSpline

# ==================== 专业船舶型值表数据 ====================
# 基于标准船舶设计原理
Lpp = 20.0  # 垂线间长 (cm)
B = 8.0     # 型宽 (cm)
D = 4.0     # 型深 (cm)
T = 2.5     # 吃水 (cm)

# 专业型值表 - 21个站号，5个水线
half_breadth = np.array([
    # 船尾部分
    [0.0, 0.8, 1.6, 2.0, 2.2],    # 站0
    [0.2, 1.0, 1.8, 2.2, 2.4],    # 站1
    [0.4, 1.2, 2.0, 2.4, 2.6],    # 站2
    [0.6, 1.4, 2.2, 2.6, 2.8],    # 站3
    [0.8, 1.6, 2.4, 2.8, 3.0],    # 站4
    
    # 船中前部
    [1.0, 1.8, 2.6, 3.0, 3.2],    # 站5
    [1.2, 2.0, 2.8, 3.2, 3.4],    # 站6
    [1.4, 2.2, 3.0, 3.4, 3.6],    # 站7
    [1.6, 2.4, 3.2, 3.6, 3.8],    # 站8
    [1.8, 2.6, 3.4, 3.8, 4.0],    # 站9
    
    # 船中 (最大宽度处)
    [2.0, 2.8, 3.6, 4.0, 4.0],    # 站10
    
    # 船中后部
    [1.8, 2.6, 3.4, 3.8, 4.0],    # 站11
    [1.6, 2.4, 3.2, 3.6, 3.8],    # 站12
    [1.4, 2.2, 3.0, 3.4, 3.6],    # 站13
    [1.2, 2.0, 2.8, 3.2, 3.4],    # 站14
    [1.0, 1.8, 2.6, 3.0, 3.2],    # 站15
    
    # 船首部分
    [0.8, 1.6, 2.4, 2.8, 3.0],    # 站16
    [0.6, 1.4, 2.2, 2.6, 2.8],    # 站17
    [0.4, 1.2, 2.0, 2.4, 2.6],    # 站18
    [0.2, 1.0, 1.8, 2.2, 2.4],    # 站19
    [0.0, 0.8, 1.6, 2.0, 2.2]     # 站20
])

# 水线高度 (从基线向上)
waterlines = np.array([0.0, 1.25, 2.5, 3.75, 5.0])
stations = np.linspace(0, Lpp, half_breadth.shape[0])

def create_professional_hull():
    """创建专业船舶3D模型"""
    print("创建专业船舶3D模型...")
    
    # 使用高质量插值
    stations_dense = np.linspace(0, Lpp, 51)
    waterlines_dense = np.linspace(0, 5.0, 21)
    
    # 创建插值函数
    f = RectBivariateSpline(stations, waterlines, half_breadth)
    half_breadth_dense = f(stations_dense, waterlines_dense)
    
    vertices = []
    edges = []
    
    # 生成顶点 - 右舷
    for i, station in enumerate(stations_dense):
        for j, waterline in enumerate(waterlines_dense):
            y = half_breadth_dense[i, j]
            vertices.append((station, y, waterline))
    
    # 生成顶点 - 左舷（对称）
    vertex_count = len(vertices)
    for i, station in enumerate(stations_dense):
        for j, waterline in enumerate(waterlines_dense):
            y = half_breadth_dense[i, j]
            vertices.append((station, -y, waterline))
    
    # 生成边结构
    num_stations = len(stations_dense)
    num_waterlines = len(waterlines_dense)
    
    # 水线边
    for i in range(num_stations):
        for j in range(num_waterlines - 1):
            # 右舷
            idx1 = i * num_waterlines + j
            idx2 = i * num_waterlines + j + 1
            edges.append((idx1, idx2))
            
            # 左舷
            idx1 = vertex_count + i * num_waterlines + j
            idx2 = vertex_count + i * num_waterlines + j + 1
            edges.append((idx1, idx2))
    
    # 站号线
    for j in range(num_waterlines):
        for i in range(num_stations - 1):
            # 右舷
            idx1 = i * num_waterlines + j
            idx2 = (i + 1) * num_waterlines + j
            edges.append((idx1, idx2))
            
            # 左舷
            idx1 = vertex_count + i * num_waterlines + j
            idx2 = vertex_count + (i + 1) * num_waterlines + j
            edges.append((idx1, idx2))
    
    # 横向连接边
    for i in range(0, num_stations, 2):  # 每隔一个站号连接
        for j in range(0, num_waterlines, 2):  # 每隔一个水线连接
            idx_right = i * num_waterlines + j
            idx_left = vertex_count + i * num_waterlines + j
            edges.append((idx_right, idx_left))
    
    print(f"专业模型: {len(vertices)}个顶点, {len(edges)}条边")
    return vertices, edges

def visualize_professional_hull(vertices, edges):
    """专业级船舶3D可视化"""
    print("生成专业级3D可视化...")
    
    vertices_array = np.array(vertices)
    
    # 创建高质量图形
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 设置专业视角
    ax.view_init(elev=20, azim=45)
    
    # 计算模型中心点，确保模型居中
    center_x = (vertices_array[:, 0].max() + vertices_array[:, 0].min()) / 2
    center_y = (vertices_array[:, 1].max() + vertices_array[:, 1].min()) / 2
    center_z = (vertices_array[:, 2].max() + vertices_array[:, 2].min()) / 2
    
    # 绘制所有边 - 使用高质量设置
    for edge in edges:
        v1, v2 = vertices_array[edge[0]], vertices_array[edge[1]]
        ax.plot([v1[0], v2[0]], [v1[1], v2[1]], [v1[2], v2[2]], 
               'b-', linewidth=0.8, alpha=0.8)
    
    # 设置坐标轴
    ax.set_xlabel('船长 (m)', fontsize=12, labelpad=10)
    ax.set_ylabel('船宽 (m)', fontsize=12, labelpad=10)
    ax.set_zlabel('型深 (m)', fontsize=12, labelpad=10)
    ax.set_title('专业船舶3D线框模型', fontsize=16, pad=20)
    
    # 计算合适的显示范围，确保模型居中
    max_range = max(
        vertices_array[:, 0].max() - vertices_array[:, 0].min(),
        vertices_array[:, 1].max() - vertices_array[:, 1].min(),
        vertices_array[:, 2].max() - vertices_array[:, 2].min()
    ) * 1.1  # 增加10%的边距
    
    # 设置居中显示范围
    ax.set_xlim(center_x - max_range/2, center_x + max_range/2)
    ax.set_ylim(center_y - max_range/2, center_y + max_range/2)
    ax.set_zlim(center_z - max_range/2, center_z + max_range/2)
    
    # 设置等比例缩放
    ax.set_box_aspect([1, 1, 1])
    
    # 专业级美化
    ax.grid(True, alpha=0.3)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('white')
    ax.yaxis.pane.set_edgecolor('white')
    ax.zaxis.pane.set_edgecolor('white')
    
    # 设置背景色
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white') # type: ignore
    
    # 添加比例尺
    scale_x = Lpp / 10
    scale_y = B / 10
    scale_z = D / 10
    ax.quiver(center_x - max_range/2.5, center_y - max_range/2.5, center_z - max_range/2.5, 
              scale_x, 0, 0, color='r', arrow_length_ratio=0.1, linewidth=2)
    ax.quiver(center_x - max_range/2.5, center_y - max_range/2.5, center_z - max_range/2.5, 
              0, scale_y, 0, color='g', arrow_length_ratio=0.1, linewidth=2)
    ax.quiver(center_x - max_range/2.5, center_y - max_range/2.5, center_z - max_range/2.5, 
              0, 0, scale_z, color='b', arrow_length_ratio=0.1, linewidth=2)
    
    plt.tight_layout()
    
    # 显示模型信息
    print(f"📊 模型信息:")
    print(f"船长 Lpp: {Lpp} cm")
    print(f"型宽 B: {B} cm")
    print(f"型深 D: {D} cm")
    print(f"吃水 T: {T} cm")
    print(f"模型中心: ({center_x:.1f}, {center_y:.1f}, {center_z:.1f})")
    
    plt.show()

def main():
    """主函数"""
    print("🚢 专业船舶3D线框可视化")
    print("=" * 50)
    print("优化显示效果，确保模型居中")
    print("=" * 50)
    
    try:
        # 创建专业船舶模型
        vertices, edges = create_professional_hull()
        
        # 可视化
        visualize_professional_hull(vertices, edges)
        
        print("\n✅ 专业级3D可视化完成!")
        print("💡 专业特性:")
        print("   - 模型精确居中显示")
        print("   - 等比例缩放，保持正确比例")
        print("   - 专业美化效果")
        print("   - 添加了比例尺指示")
        print("   - 基于标准船舶设计原理")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()