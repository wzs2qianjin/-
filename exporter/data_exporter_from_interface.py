#!/usr/bin/env python3
"""
数据导出器 - 基于hull_interface数据结构
将HullBasicParams、HullCoeffs、HydrostaticData等导出为CSV/TXT格式
"""

import csv
import json
from datetime import datetime
from typing import List
from hull_interface import (
    HullBasicParams, HullCoeffs, HydrostaticData, StabilityData, 
    CargoHoldData, ResistanceData, ReportData
)


class DataExporter:
    """基于hull_interface的数据导出器"""
    
    @staticmethod
    def export_basic_params_to_csv(basic_params: HullBasicParams, filepath: str):
        """导出船体基础参数到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['船体基础参数'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'参数来源: {basic_params.param_source}'])
                writer.writerow([])
                
                # 写入表头
                writer.writerow(['参数名称', '数值', '单位', '说明'])
                
                # 基础参数数据
                basic_data = [
                    ('垂线间长 Lpp', f"{basic_params.Lpp:.3f}", 'm', '两垂线间的长度'),
                    ('型宽 B', f"{basic_params.B:.3f}", 'm', '船体最大宽度'),
                    ('型深 D', f"{basic_params.D:.3f}", 'm', '从基线到甲板的深度'),
                    ('吃水 T', f"{basic_params.T:.3f}", 'm', '设计吃水深度'),
                    ('排水量 Δ', f"{basic_params.Delta:.1f}", 't', '船舶总重量')
                ]
                
                # 可选参数
                if basic_params.Loa is not None:
                    basic_data.append(('总长 Loa', f"{basic_params.Loa:.3f}", 'm', '船舶总长度'))
                
                # 写入数据
                for param_name, value, unit, description in basic_data:
                    writer.writerow([param_name, value, unit, description])
                
                writer.writerow([])
                writer.writerow(['注：数据基于用户输入或文件导入'])
            
            print(f"✓ 船体基础参数已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 船体基础参数导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_hull_coeffs_to_csv(hull_coeffs: HullCoeffs, filepath: str):
        """导出船形系数到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['船形系数数据'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'系数版本: {hull_coeffs.coeff_version}'])
                writer.writerow([])
                
                # 写入表头
                writer.writerow(['系数名称', '符号', '数值', '计算公式', '说明'])
                
                # 船形系数数据
                coeff_data = [
                    ('方形系数', 'Cb', f"{hull_coeffs.Cb:.4f}", '∇ / (Lpp×B×T)', '表征船体丰满程度'),
                    ('棱形系数', 'Cp', f"{hull_coeffs.Cp:.4f}", '∇ / (Am×Lpp)', '表征船体纵向棱形程度'),
                    ('水线面系数', 'Cw', f"{hull_coeffs.Cw:.4f}", 'Aw / (Lpp×B)', '表征水线面丰满程度'),
                    ('中横剖面系数', 'Cm', f"{hull_coeffs.Cm:.4f}", 'Am / (B×T)', '表征中横剖面丰满程度')
                ]
                
                # 写入数据
                for coeff_name, symbol, value, formula, description in coeff_data:
                    writer.writerow([coeff_name, symbol, value, formula, description])
                
                writer.writerow([])
                writer.writerow(['注：船形系数为无量纲参数'])
            
            print(f"✓ 船形系数已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 船形系数导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_hydrostatic_to_csv(hydro_data: HydrostaticData, filepath: str):
        """导出静水力数据到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['静水力参数数据'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'数据版本: {hydro_data.hydro_version}'])
                writer.writerow([])
                
                # 写入表头
                writer.writerow(['参数名称', '数值', '单位', '说明'])
                
                # 静水力数据
                hydrostatic_data = [
                    ('排水体积 ▽', f"{hydro_data.displacement_volume:.1f}", 'm³', '船舶排水体积'),
                    ('浮心纵向位置 LCB', f"{hydro_data.LCB:.3f}", 'm', '距船中距离，向前为正'),
                    ('浮心垂向位置 VCB', f"{hydro_data.VCB:.3f}", 'm', '距基线高度'),
                    ('每厘米吃水吨数 TPC', f"{hydro_data.TPC:.2f}", 't/cm', '吃水变化1cm的排水量变化'),
                    ('横稳心半径 BM', f"{hydro_data.BM:.3f}", 'm', '浮心到横稳心的距离')
                ]
                
                # 写入数据
                for param_name, value, unit, description in hydrostatic_data:
                    writer.writerow([param_name, value, unit, description])
                
                writer.writerow([])
                writer.writerow(['注：基于梯形积分法计算'])
            
            print(f"✓ 静水力数据已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 静水力数据导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_resistance_to_csv(resistance_data: ResistanceData, filepath: str):
        """导出阻力数据到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['阻力与有效功率数据'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'计算方法: {resistance_data.method}'])
                writer.writerow([])
                
                # 写入表头
                writer.writerow(['航速 (kn)', '总阻力 (kN)', '有效功率 (kW)', '备注'])
                
                # 写入数据
                for i in range(len(resistance_data.speed_list)):
                    speed = resistance_data.speed_list[i]
                    resistance = resistance_data.total_resistance_list[i]
                    power = resistance_data.effective_power_list[i]
                    remark = '设计航速' if i == len(resistance_data.speed_list) // 2 else ''
                    
                    writer.writerow([
                        f"{speed:.1f}",
                        f"{resistance:.1f}",
                        f"{power:.1f}",
                        remark
                    ])
                
                writer.writerow([])
                writer.writerow(['注：基于Holtrop-Mennen方法计算'])
            
            print(f"✓ 阻力数据已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 阻力数据导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_stability_to_csv(stability_data: StabilityData, filepath: str):
        """导出稳性数据到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['稳性分析数据'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([f'装载工况: {stability_data.loading_condition}'])
                writer.writerow([])
                
                # 静水力曲线数据
                writer.writerow(['静水力曲线数据 (吃水-排水体积)'])
                writer.writerow(['吃水 T (m)', '排水体积 ▽ (m³)'])
                
                for draft, volume in stability_data.hydro_curve:
                    writer.writerow([f"{draft:.2f}", f"{volume:.1f}"])
                
                writer.writerow([])
                
                # GZ曲线数据
                writer.writerow(['静稳性臂 GZ 曲线数据'])
                writer.writerow(['横倾角 θ (°)', '稳性臂 GZ (m)'])
                
                for angle, gz in stability_data.gz_curve:
                    writer.writerow([f"{angle}", f"{gz:.3f}"])
                
                writer.writerow([])
                writer.writerow(['注：基于小角度静稳性假设计算'])
            
            print(f"✓ 稳性数据已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 稳性数据导出失败: {str(e)}")
            return False
    
    @staticmethod
    def export_cargo_to_csv(cargo_data: List[CargoHoldData], filepath: str):
        """导出舱容数据到CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入文件头
                writer.writerow(['舱室容量数据'])
                writer.writerow([f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow(['计算方法: 长方体近似法'])
                writer.writerow([])
                
                # 写入表头
                writer.writerow(['舱室名称', '纵向范围 (m)', '横向范围 (m)', '容积 (m³)', '位置描述'])
                
                total_volume = 0
                for cargo in cargo_data:
                    x_range = f"{cargo.hold_position[0]:.1f}-{cargo.hold_position[1]:.1f}"
                    y_range = f"{cargo.hold_position[2]:.1f}-{cargo.hold_position[3]:.1f}"
                    position_desc = DataExporter._get_cargo_position_description(cargo.hold_position)
                    
                    writer.writerow([
                        cargo.hold_name,
                        x_range,
                        y_range,
                        f"{cargo.hold_volume:.1f}",
                        position_desc
                    ])
                    total_volume += cargo.hold_volume
                
                # 写入总计行
                writer.writerow(['-' * 20, '-' * 15, '-' * 15, '-' * 10, '-' * 15])
                writer.writerow(['总计', '-', '-', f"{total_volume:.1f}", '-'])
                
                writer.writerow([])
                writer.writerow(['注：基于长方体近似法计算'])
            
            print(f"✓ 舱容数据已导出: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 舱容数据导出失败: {str(e)}")
            return False
    
    @staticmethod
    def _get_cargo_position_description(position: tuple) -> str:
        """根据舱室位置坐标返回描述"""
        x_start, x_end, y_start, y_end = position
        descriptions = []
        
        # 纵向位置描述
        if x_start >= 0:
            descriptions.append("前部")
        elif x_end <= 0:
            descriptions.append("后部")
        else:
            descriptions.append("中部")
        
        # 横向位置描述
        if y_start >= 0 and y_end >= 0:
            descriptions.append("右舷")
        elif y_start <= 0 and y_end <= 0:
            descriptions.append("左舷")
        else:
            descriptions.append("船中")
        
        return " ".join(descriptions)
    
    @staticmethod
    def export_all_to_json(report_data: ReportData, filepath: str):
        """导出所有数据到JSON"""
        try:
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'version': '1.0',
                    'system': '船舶性能分析系统'
                },
                'basic_parameters': {
                    'Lpp': report_data.basic_params.Lpp,
                    'B': report_data.basic_params.B,
                    'D': report_data.basic_params.D,
                    'T': report_data.basic_params.T,
                    'Delta': report_data.basic_params.Delta,
                    'Loa': report_data.basic_params.Loa,
                    'param_source': report_data.basic_params.param_source
                },
                'hull_coefficients': {
                    'Cb': report_data.hull_coeffs.Cb,
                    'Cp': report_data.hull_coeffs.Cp,
                    'Cw': report_data.hull_coeffs.Cw,
                    'Cm': report_data.hull_coeffs.Cm,
                    'coeff_version': report_data.hull_coeffs.coeff_version
                },
                'hydrostatic_data': {
                    'displacement_volume': report_data.hydro_data.displacement_volume,
                    'LCB': report_data.hydro_data.LCB,
                    'VCB': report_data.hydro_data.VCB,
                    'TPC': report_data.hydro_data.TPC,
                    'BM': report_data.hydro_data.BM,
                    'hydro_version': report_data.hydro_data.hydro_version
                },
                'resistance_data': {
                    'speed_list': report_data.resistance_data.speed_list,
                    'total_resistance_list': report_data.resistance_data.total_resistance_list,
                    'effective_power_list': report_data.resistance_data.effective_power_list,
                    'method': report_data.resistance_data.method
                },
                'stability_data': {
                    'hydro_curve': report_data.stability_data.hydro_curve,
                    'gz_curve': report_data.stability_data.gz_curve,
                    'loading_condition': report_data.stability_data.loading_condition
                },
                'cargo_data': [
                    {
                        'hold_name': cargo.hold_name,
                        'hold_position': cargo.hold_position,
                        'hold_volume': cargo.hold_volume
                    } for cargo in report_data.cargo_data
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 完整数据已导出(JSON): {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ JSON数据导出失败: {str(e)}")
            return False


def demo_export_all_data():
    """演示导出所有数据"""
    from word_report_from_interface import create_sample_report_data
    
    print("开始导出所有数据格式...")
    
    # 创建示例数据
    report_data = create_sample_report_data()
    exporter = DataExporter()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 导出各种格式
    exports = [
        ('CSV', lambda: exporter.export_basic_params_to_csv(
            report_data.basic_params, f'船体基础参数_{timestamp}.csv')),
        ('CSV', lambda: exporter.export_hull_coeffs_to_csv(
            report_data.hull_coeffs, f'船形系数_{timestamp}.csv')),
        ('CSV', lambda: exporter.export_hydrostatic_to_csv(
            report_data.hydro_data, f'静水力数据_{timestamp}.csv')),
        ('CSV', lambda: exporter.export_resistance_to_csv(
            report_data.resistance_data, f'阻力数据_{timestamp}.csv')),
        ('CSV', lambda: exporter.export_stability_to_csv(
            report_data.stability_data, f'稳性数据_{timestamp}.csv')),
        ('CSV', lambda: exporter.export_cargo_to_csv(
            report_data.cargo_data, f'舱容数据_{timestamp}.csv')),
        ('JSON', lambda: exporter.export_all_to_json(
            report_data, f'完整数据_{timestamp}.json'))
    ]
    
    success_count = 0
    for format_name, export_func in exports:
        if export_func():
            success_count += 1
            print(f"  ✓ {format_name}格式导出成功")
        else:
            print(f"  ✗ {format_name}格式导出失败")
    
    print(f"\n导出完成: {success_count}/{len(exports)} 个文件成功生成")
    print("📁 请在当前目录查看生成的导出文件")


if __name__ == '__main__':
    demo_export_all_data()