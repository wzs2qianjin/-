# 模块文件名：gui_param_input.py
from hull_interface import HullBasicParams, ParamCheckResult

def create_param_input_window() -> None:
    """
    功能：创建参数输入窗口（用Qt Designer拖拽生成界面，绑定“确认”按钮事件）
    输入：无
    输出：无（窗口显示在屏幕上）
    按钮事件逻辑：
    1. 读取界面上输入框的数值（如Lpp=100, B=20...）
    2. 构造HullBasicParams对象
    3. 调用子模块2的check_hull_params函数进行校验
    4. 若校验失败（is_valid=False），在界面上显示error_msg
    5. 若校验成功，将valid_params传递给子模块2的save_valid_params函数存储
    """
    pass  # 开发者需实现：用PyQt绘制输入框、按钮，绑定事件

def get_user_input_params() -> HullBasicParams:
    """
    功能：获取用户输入的参数（供子模块1内部调用，传递给子模块2）
    输入：无（从GUI输入框读取）
    输出：HullBasicParams对象（未校验的原始参数）
    """
    pass

def show_param_error(error_msg: str) -> None:
    """
    功能：在GUI上显示参数错误提示（如弹窗、红色文字）
    输入：error_msg（子模块2返回的错误信息）
    输出：无
    """
    pass