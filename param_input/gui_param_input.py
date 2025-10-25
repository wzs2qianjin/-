# gui_param_input.py
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QEvent
import sys
from param_input.ui_param_input import Ui_MainWindow
from core. hull_interface import HullBasicParams, ParamCheckResult

# 全局变量:存储验证通过的参数
GLOBAL_VALID_PARAMS = None


def check_hull_params(params: HullBasicParams) -> ParamCheckResult:
    """船体参数校验逻辑(适配HullBasicParams结构)"""
    errors = []
    # 基础参数非空校验(Lpp、B、D、T、Delta为必填项)
    if not all([params.Lpp, params.B, params.D, params.T, params.Delta]):
        errors.append("垂线间长、船宽、型深、吃水、排水量为必填项")

    try:
        # 转换为数值并校验逻辑关系
        lpp = float(params.Lpp)
        b = float(params.B)
        d = float(params.D)
        t = float(params.T)
        delta = float(params.Delta)
        loa = float(params.Loa) if params.Loa else None

        # 数值范围校验
        if lpp <= 0:
            errors.append("垂线间长(Lpp)必须大于0")
        if b <= 0 or b >= lpp:
            errors.append("船宽(B)必须>0且<垂线间长(Lpp)")
        if d <= 0 or d >= lpp:
            errors.append("型深(D)必须>0且<垂线间长(Lpp)")
        if t <= 0 or t >= d:
            errors.append("吃水(T)必须>0且<型深(D)")
        if delta <= 0:
            errors.append("排水量(Delta)必须>0")
        if loa is not None and (loa <= 0 or loa < lpp):
            errors.append("总长(Loa)必须>0且≥垂线间长(Lpp)(若填写)")
    except ValueError:
        errors.append("输入必须为有效数字(整数或小数)")

    # 构造校验结果
    if errors:
        return ParamCheckResult(
            is_valid=False,
            error_msg=";".join(errors),
            valid_params=None
        )
    return ParamCheckResult(
        is_valid=True,
        error_msg="",
        valid_params=params
    )


def save_valid_params(valid_params: HullBasicParams) -> None:
    """存储验证通过的参数到全局变量"""
    global GLOBAL_VALID_PARAMS
    GLOBAL_VALID_PARAMS = valid_params
    print(f"已存储有效参数:{valid_params}")


class ParamInputLogic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI控件
        self.init_ui_state()  # 初始化UI状态
        self.bind_events()  # 绑定交互事件
        self._set_input_filter()  # 设置输入过滤
        self._install_event_filters()  # 安装事件过滤器

    def update_status_message(self, message: str):
        """安全更新状态栏消息"""
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(message)
            
    def init_ui_state(self):
        """初始化UI状态:清空输入框和状态栏"""
        self.le_lpp.clear()
        self.le_b.clear()
        self.le_d.clear()
        self.le_t.clear()
        self.le_delta.clear()
        self.update_status_message("请输入船体参数并点击确定")

    def bind_events(self):
        """绑定所有交互事件"""
        # 按钮事件
        self.btn_confirm.clicked.connect(self.on_confirm_click)
        self.btn_reset.clicked.connect(self.on_reset_click)

        # 输入框文本变化事件(实时验证)
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        for edit in input_edits:
            edit.textChanged.connect(self.on_text_changed)

    def _set_input_filter(self):
        """设置输入框过滤器:仅允许数字和小数点"""
        # 正则表达式:允许非负整数或小数(支持整数部分、可选小数部分)
        float_reg = QtCore.QRegExp(r"^[0-9]+(\.[0-9]*)?$")
        float_validator = QtGui.QRegExpValidator(float_reg, self)
        # 为所有参数输入框应用过滤器
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        for edit in input_edits:
            edit.setValidator(float_validator)
            # 设置输入框对齐方式为右对齐(数字输入习惯)
            edit.setAlignment(Qt.AlignRight) # type: ignore

    def _install_event_filters(self):
        """为输入框安装事件过滤器(处理焦点事件)"""
        input_edits = [self.le_lpp, self.le_b, self.le_d, self.le_t, self.le_delta]
        for edit in input_edits:
            edit.installEventFilter(self)

    def eventFilter(self, obj, event):
        """事件过滤器:处理输入框焦点提示"""
        if event.type() == QEvent.FocusIn: # type: ignore
            # 焦点进入时显示参数说明
            param_hints = {
                self.le_lpp: "垂线间长(Lpp):船舶首垂线与尾垂线之间的水平距离,必须大于0",
                self.le_b: "船宽(B):船舶最大横向宽度,必须>0且小于垂线间长",
                self.le_d: "型深(D):船底基线到甲板边线的垂直距离,必须>0且小于垂线间长",
                self.le_t: "吃水(T):船底基线到水面的垂直距离,必须>0且小于型深",
                self.le_delta: "排水量(Delta):船舶排开水的重量,单位为吨,必须大于0"
            }
            if obj in param_hints:
                self.update_status_message(param_hints[obj])
        elif event.type() == QEvent.FocusOut: # type: ignore
            # 焦点离开时恢复默认提示(如果输入为空)
            if not obj.text().strip():
                self.update_status_message("请输入船体参数并点击确定")
        return super().eventFilter(obj, event)

    def on_text_changed(self):
        """处理输入框文本变化:实时检查输入有效性"""
        sender = self.sender()  # 获取触发事件的输入框
        # 添加空值检查
        if sender is None:
            return
        text = sender.text().strip() # type: ignore

        if not text:
            # 空输入提示(必填项)
            self.update_status_message(f"{self._get_param_name(sender)}为必填项,请输入有效值")
        elif text == ".":
            # 不完整的小数输入提示
            self.update_status_message(f"{self._get_param_name(sender)}输入不完整,请补充数字")
        else:
            # 有效输入提示
            self.update_status_message(f"{self._get_param_name(sender)}输入有效")

    def _get_param_name(self, edit):
        """获取输入框对应的参数名称"""
        # 添加空值检查
        if edit is None:
            return "参数"
        
        param_names = {
            self.le_lpp: "垂线间长(Lpp)",
            self.le_b: "船宽(B)",
            self.le_d: "型深(D)",
            self.le_t: "吃水(T)",
            self.le_delta: "排水量(Delta)"
        }
        return param_names.get(edit, "参数")

    def on_confirm_click(self):
        """处理确定按钮点击事件:获取输入→校验→反馈结果"""
        # 获取输入框内容(去除首尾空格)
        lpp = self.le_lpp.text().strip()
        b = self.le_b.text().strip()
        d = self.le_d.text().strip()
        t = self.le_t.text().strip()
        delta = self.le_delta.text().strip()

        # 构造船体基本参数对象(Loa暂未提供输入框,设为None)
        params = HullBasicParams(
            Lpp=lpp,
            B=b,
            D=d,
            T=t,
            Delta=delta,
            Loa=None  # UI中未包含总长输入框,暂不支持
        )

        # 执行参数校验
        check_result = check_hull_params(params)

        # 处理校验结果
        if check_result.is_valid and check_result.valid_params is not None:
            # 校验通过:保存参数并显示成功信息
            save_valid_params(check_result.valid_params)
            self.update_status_message("参数验证通过,已保存")
            QMessageBox.information(
                self, "成功",
                f"参数验证通过:\n"
                f"垂线间长:{lpp}m\n"
                f"船宽:{b}m\n"
                f"型深:{d}m\n"
                f"吃水:{t}m\n"
                f"排水量:{delta}t"
            )
        else:
            # 校验失败:显示错误信息
            self.update_status_message("参数验证失败,请检查输入")
            QMessageBox.critical(
                self, "输入错误",
                f"参数验证失败:\n{check_result.error_msg}"
            )

    def on_reset_click(self):
        """处理重置按钮点击事件:清空所有输入"""
        self.init_ui_state()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParamInputLogic()
    window.setWindowTitle("船舶设计系统 - 参数输入")  # 设置窗口标题
    window.show()
    sys.exit(app.exec_())