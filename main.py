# main.py - 合并船舶参数输入GUI与校验存储模块
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
import sys
from typing import Optional
# 导入依赖接口和UI布局
# 导入 ui_param_input
from param_input.ui_param_input import Ui_MainWindow
# 导入 hull_interface
from core.hull_interface import HullBasicParams, ParamCheckResult


# ------------------------------
# 任务单元2核心：参数存储管理类（单例模式，确保全局参数唯一）
# ------------------------------
class HullParamStore:
    """
    船体参数存储与全局访问类
    功能：1. 保存校验通过的参数 2. 为后续2D/3D模块提供参数获取接口 3. 确保参数版本一致性
    """
    _instance = None  # 单例实例
    _valid_params: Optional[HullBasicParams] = None  # 存储校验通过的参数

    def __new__(cls):
        # 单例模式：确保全局只有一个参数存储实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save_valid_params(self, params: HullBasicParams) -> None:
        """保存校验通过的船体参数"""
        self._valid_params = params
        print(f"[存储日志] 已保存有效参数：\n{params}")

    def get_valid_params(self) -> Optional[HullBasicParams]:
        """获取校验通过的参数（供2D型线/3D模型模块调用）"""
        return self._valid_params

    def clear_params(self) -> None:
        """清空存储的参数（重置时使用）"""
        self._valid_params = None
        print(f"[存储日志] 已清空参数")


# ------------------------------
# 任务单元2核心：参数校验函数（遵循船舶设计规则）
# ------------------------------
def check_hull_params(params: HullBasicParams) -> ParamCheckResult:
    """
    船体参数合法性校验（任务单元2核心逻辑）
    校验规则：1. 必填参数非空 2. 数值为有效数字 3. 符合船舶设计基本逻辑（船长>船宽、吃水<型深等）
    :param params: 待校验的参数对象（来自GUI输入）
    :return: 校验结果（含是否合格、错误信息、有效参数）
    """
    error_messages = []

    # 1. 第一步：必填参数非空校验（任务单元1+2要求）
    required_fields = [params.Lpp, params.B, params.D, params.T, params.Delta]
    if not all(field.strip() for field in required_fields if field is not None):
        error_messages.append("垂线间长（Lpp）、船宽（B）、型深（D）、吃水（T）、排水量（Delta）为必填项，不可为空")

    try:
        # 2. 第二步：数据类型转换（字符串→数值）
        lpp = float(params.Lpp)
        b = float(params.B)
        d = float(params.D)
        t = float(params.T)
        delta = float(params.Delta)
        loa = float(params.Loa) if (params.Loa and params.Loa.strip()) else None

        # 3. 第三步：船舶设计核心规则校验（任务单元2要求）
        # 长度类参数必须为正数
        if lpp <= 0:
            error_messages.append(f"垂线间长（Lpp={lpp}m）必须大于0")
        if b <= 0:
            error_messages.append(f"船宽（B={b}m）必须大于0")
        if d <= 0:
            error_messages.append(f"型深（D={d}m）必须大于0")
        if t <= 0:
            error_messages.append(f"吃水（T={t}m）必须大于0")
        if delta <= 0:
            error_messages.append(f"排水量（Delta={delta}t）必须大于0")

        # 几何逻辑校验（船长>船宽、吃水<型深等）
        if b >= lpp:
            error_messages.append(f"船宽（B={b}m）必须小于垂线间长（Lpp={lpp}m）")
        if d >= lpp:
            error_messages.append(f"型深（D={d}m）必须小于垂线间长（Lpp={lpp}m）")
        if t >= d:
            error_messages.append(f"吃水（T={t}m）必须小于型深（D={d}m）")

        # 可选参数：总长（Loa）校验（若用户输入）
        if loa is not None:
            if loa <= 0:
                error_messages.append(f"总长（Loa={loa}m）必须大于0")
            if loa < lpp:
                error_messages.append(f"总长（Loa={loa}m）必须大于等于垂线间长（Lpp={lpp}m）")

    except ValueError:
        # 捕获非数字输入错误（任务单元1要求）
        error_messages.append("输入必须为有效数字（支持整数或小数，如100、20.5）")

    # 4. 构造校验结果（任务单元1+2要求）
    if error_messages:
        return ParamCheckResult(
            is_valid=False,
            error_msg="；".join(error_messages),
            valid_params=None
        )
    return ParamCheckResult(
        is_valid=True,
        error_msg="参数校验通过",
        valid_params=params
    )


# ------------------------------
# 任务单元1核心：GUI界面逻辑类（交互+输入处理）
# ------------------------------
class HullParamInputWindow(QMainWindow, Ui_MainWindow):
    """
    船体参数输入GUI窗口类
    功能：1. 显示参数输入界面 2. 处理用户输入（过滤+转换）3. 触发校验与结果反馈 4. 联动参数存储
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI布局（来自ui_param_input.py）
        self.param_store = HullParamStore()  # 初始化参数存储实例
        self.init_ui_state()  # 初始化UI初始状态
        self.bind_events()  # 绑定按钮交互事件
        self.set_input_filters()  # 设置输入框过滤（仅允许数字）

    def init_ui_state(self):
        """初始化UI状态：清空输入框、设置状态栏提示、禁用确认按钮"""
        # 清空所有必填参数输入框
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        for edit in input_edits:
            edit.clear()
        # 清空参数存储
        self.param_store.clear_params()
        # 状态栏初始提示
        self.statusBar().showMessage("请输入船体基本参数（带*为必填项）")
        # 初始禁用确认按钮（需所有输入框填完才启用）
        self.btn_confirm.setEnabled(False)

    def bind_events(self):
        """绑定按钮点击事件：确认输入、重置输入"""
        self.btn_confirm.clicked.connect(self.handle_confirm_input)  # 确认按钮
        self.btn_reset.clicked.connect(self.init_ui_state)  # 重置按钮（复用初始化方法）

    def set_input_filters(self):
        """设置输入框过滤器：仅允许输入非负整数/小数（符合参数数值要求）"""
        # 正则表达式：匹配非负整数（如100）或小数（如20.5、30.）
        float_regex = QtCore.QRegExp(r"^[0-9]+(\.[0-9]*)?$")
        float_validator = QtGui.QRegExpValidator(float_regex, self)

        # 为所有必填参数输入框应用过滤器
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        for edit in input_edits:
            edit.setValidator(float_validator)
            edit.setAlignment(Qt.AlignRight)  # 数字输入右对齐（符合用户习惯）
            # 输入变化时实时检查是否启用确认按钮（任务单元1：界面状态控制）
            edit.textChanged.connect(self.update_confirm_button_state)

    def update_confirm_button_state(self):
        """实时检查输入框状态，所有必填项填完后启用确认按钮（提升用户体验）"""
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        # 所有输入框均有非空内容时启用按钮
        all_filled = all(edit.text().strip() != "" for edit in input_edits)
        self.btn_confirm.setEnabled(all_filled)

    def handle_confirm_input(self):
        """处理“确认输入”按钮逻辑：获取输入→构造参数对象→校验→存储/反馈"""
        # 1. 获取输入框内容（去除首尾空格）
        lpp_input = self.le_lpp.text().strip()
        b_input = self.le_b.text().strip()
        d_input = self.le_d.text().strip()
        t_input = self.le_t.text().strip()
        delta_input = self.le_delta.text().strip()
        loa_input = None  # 暂未在UI中提供总长输入框，可后续扩展

        # 2. 构造参数对象（遵循hull_interface.py定义的标准结构）
        input_params = HullBasicParams(
            Lpp=lpp_input,
            B=b_input,
            D=d_input,
            T=t_input,
            Delta=delta_input,
            Loa=loa_input,
            param_source="user_input"  # 标记参数来源为“用户输入”
        )

        # 3. 调用校验函数执行合法性检查
        check_result = check_hull_params(input_params)

        # 4. 根据校验结果处理：存储参数或显示错误
        if check_result.is_valid:
            # 校验通过：存储参数+显示成功反馈（任务单元1+2要求）
            self.param_store.save_valid_params(check_result.valid_params)
            # 状态栏提示
            self.statusBar().showMessage(f"✅ {check_result.error_msg}，可进行后续建模")
            # 弹出成功对话框（展示详细参数）
            QMessageBox.information(
                self, "参数校验通过",
                f"以下参数已成功保存，可进入2D/3D建模环节：\n\n"
                f"• 垂线间长（Lpp）：{lpp_input} m\n"
                f"• 船宽（B）：{b_input} m\n"
                f"• 型深（D）：{d_input} m\n"
                f"• 吃水（T）：{t_input} m\n"
                f"• 排水量（Delta）：{delta_input} t"
            )
        else:
            # 校验失败：显示错误信息（任务单元1要求）
            self.statusBar().showMessage("❌ 参数校验失败，请修正输入")
            QMessageBox.critical(
                self, "参数输入错误",
                f"校验失败原因：\n{check_result.error_msg}\n\n"
                f"请按以下规则修正：\n"
                f"1. 所有必填项不可为空\n"
                f"2. 输入必须为非负数字（如100、20.5）\n"
                f"3. 满足船舶设计逻辑（船宽<船长、吃水<型深等）"
            )


# ------------------------------
# 应用入口：启动GUI窗口
# ------------------------------
if __name__ == "__main__":
    # 初始化PyQt应用
    app = QApplication(sys.argv)
    # 创建参数输入窗口实例
    window = HullParamInputWindow()
    # 设置窗口标题（符合任务单元1界面要求）
    window.setWindowTitle("船舶三维建模系统 - 船体参数输入与校验")
    # 显示窗口
    window.show()
    # 执行应用事件循环
    sys.exit(app.exec_())