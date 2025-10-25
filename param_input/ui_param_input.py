# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'param_input.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
# 优化方向:布局规整化、视觉美化、交互增强
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)  # 保持原窗口大小，布局自动适配
        MainWindow.setMinimumSize(700, 500)  # 设置最小窗口尺寸，避免挤压

        # 中心部件与主布局(替代绝对坐标)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.main_layout = QHBoxLayout(self.centralwidget)  # 主水平布局:左(参数区)+ 右(预览区)
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # 主布局边距
        self.main_layout.setSpacing(20)  # 左右区域间距

        # ---------------------- 左侧:船体参数输入区(规整分组) ----------------------
        self.param_group = QGroupBox("船体基本参数(带*为必填项)", self.centralwidget)
        self.param_group.setObjectName("param_group")
        self.param_layout = QVBoxLayout(self.param_group)  # 参数区垂直布局
        self.param_layout.setContentsMargins(30, 20, 30, 20)
        self.param_layout.setSpacing(18)  # 参数项之间的间距

        # 1. 船长(必填)
        self.row_lpp = QHBoxLayout()  # 单行布局:标签 + 输入框
        self.label_2 = QtWidgets.QLabel(self.param_group)
        self.label_2.setText("<html><body><span style='font-size:10pt;'>船长(m)</span><span style='color:red;'>*</span></body></html>")
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # type: ignore # 标签右对齐
        self.label_2.setFixedWidth(80)  # 固定标签宽度，保证对齐

        self.le_lpp = QtWidgets.QLineEdit(self.param_group)
        self.le_lpp.setObjectName("le_lpp")
        self.le_lpp.setPlaceholderText("示例:120.5")  # 输入提示
        self.le_lpp.setFixedWidth(150)  # 固定输入框宽度
        self.le_lpp.setFixedHeight(30)  # 增加输入框高度，提升点击感

        self.row_lpp.addWidget(self.label_2)
        self.row_lpp.addSpacing(10)  # 标签与输入框间距
        self.row_lpp.addWidget(self.le_lpp)
        self.param_layout.addLayout(self.row_lpp)

        # 2. 船宽(必填)
        self.row_b = QHBoxLayout()
        self.label_3 = QtWidgets.QLabel(self.param_group)
        self.label_3.setText("<html><body><span style='font-size:10pt;'>船宽(m)</span><span style='color:red;'>*</span></body></html>")
        self.label_3.setObjectName("label_3")
        self.label_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter) # type: ignore
        self.label_3.setFixedWidth(80)

        self.le_b = QtWidgets.QLineEdit(self.param_group)
        self.le_b.setObjectName("le_b")
        self.le_b.setPlaceholderText("示例:18.2")
        self.le_b.setFixedWidth(150)
        self.le_b.setFixedHeight(30)

        self.row_b.addWidget(self.label_3)
        self.row_b.addSpacing(10)
        self.row_b.addWidget(self.le_b)
        self.param_layout.addLayout(self.row_b)

        # 3. 型深(必填)
        self.row_d = QHBoxLayout()
        self.label_4 = QtWidgets.QLabel(self.param_group)
        self.label_4.setText("<html><body><span style='font-size:10pt;'>型深(m)</span><span style='color:red;'>*</span></body></html>")
        self.label_4.setObjectName("label_4")
        self.label_4.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter) # type: ignore
        self.label_4.setFixedWidth(80)

        self.le_d = QtWidgets.QLineEdit(self.param_group)
        self.le_d.setObjectName("le_d")
        self.le_d.setPlaceholderText("示例:9.5")
        self.le_d.setFixedWidth(150)
        self.le_d.setFixedHeight(30)

        self.row_d.addWidget(self.label_4)
        self.row_d.addSpacing(10)
        self.row_d.addWidget(self.le_d)
        self.param_layout.addLayout(self.row_d)

        # 4. 吃水(必填)
        self.row_t = QHBoxLayout()
        self.label_5 = QtWidgets.QLabel(self.param_group)
        self.label_5.setText("<html><body><span style='font-size:10pt;'>吃水(m)</span><span style='color:red;'>*</span></body></html>")
        self.label_5.setObjectName("label_5")
        self.label_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter) # type: ignore
        self.label_5.setFixedWidth(80)

        self.le_t = QtWidgets.QLineEdit(self.param_group)
        self.le_t.setObjectName("le_t")
        self.le_t.setPlaceholderText("示例:6.8")
        self.le_t.setFixedWidth(150)
        self.le_t.setFixedHeight(30)

        self.row_t.addWidget(self.label_5)
        self.row_t.addSpacing(10)
        self.row_t.addWidget(self.le_t)
        self.param_layout.addLayout(self.row_t)

        # 5. 排水量(必填)
        self.row_delta = QHBoxLayout()
        self.label_6 = QtWidgets.QLabel(self.param_group)
        self.label_6.setText("<html><body><span style='font-size:10pt;'>排水量(t)</span><span style='color:red;'>*</span></body></html>")
        self.label_6.setObjectName("label_6")
        self.label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter) # type: ignore
        self.label_6.setFixedWidth(80)

        self.le_delta = QtWidgets.QLineEdit(self.param_group)
        self.le_delta.setObjectName("le_delta")
        self.le_delta.setPlaceholderText("示例:8500")
        self.le_delta.setFixedWidth(150)
        self.le_delta.setFixedHeight(30)

        self.row_delta.addWidget(self.label_6)
        self.row_delta.addSpacing(10)
        self.row_delta.addWidget(self.le_delta)
        self.param_layout.addLayout(self.row_delta)

        # 按钮区(确定+重置)
        self.btn_layout = QHBoxLayout()
        self.btn_reset = QtWidgets.QPushButton(self.param_group)
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setFixedSize(80, 35)  # 固定按钮大小

        self.btn_confirm = QtWidgets.QPushButton(self.param_group)
        self.btn_confirm.setObjectName("btn_confirm")
        self.btn_confirm.setFixedSize(80, 35)

        self.btn_layout.addWidget(self.btn_reset)
        self.btn_layout.addSpacing(20)
        self.btn_layout.addWidget(self.btn_confirm)
        self.btn_layout.setAlignment(QtCore.Qt.AlignCenter)  # type: ignore # 按钮居中
        self.param_layout.addSpacing(30)  # 与上方参数区的间距
        self.param_layout.addLayout(self.btn_layout)

        # ---------------------- 右侧:保留原ColumnView(预览/辅助区) ----------------------
        self.right_layout = QVBoxLayout()
        self.columnView_2 = QtWidgets.QColumnView(self.centralwidget)
        self.columnView_2.setObjectName("columnView_2")
        self.columnView_2.setMinimumWidth(300)  # 保证右侧区域不被挤压

        # 右侧标题(明确区域功能)
        self.right_title = QtWidgets.QLabel(self.centralwidget)
        self.right_title.setText("<html><body><p style='font-size:12pt; font-weight:600; color:#2c3e50;'>参数预览/建模辅助区</p></body></html>")
        self.right_title.setAlignment(QtCore.Qt.AlignCenter) # type: ignore

        self.right_layout.addWidget(self.right_title)
        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(self.columnView_2)

        # ---------------------- 组装主布局 ----------------------
        self.main_layout.addWidget(self.param_group, stretch=1)  # 左侧占1份宽度
        self.main_layout.addLayout(self.right_layout, stretch=5)  # 右侧占2份宽度(更宽，适合预览)

        MainWindow.setCentralWidget(self.centralwidget)

        # 菜单栏与状态栏(保留原结构，优化样式)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))  # 增加菜单栏高度，提升点击感
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # ---------------------- 全局样式表(核心美化) ----------------------
        self.set_style(MainWindow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def set_style(self, MainWindow):
        """设置全局QSS样式"""
        style = """
            /* 窗口背景:浅灰渐变，避免单调 */
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f7fa, stop:1 #e4e9f2);
            }

            /* 参数分组框:白色背景+阴影，突出区域 */
            QGroupBox {
                font-size: 13pt;
                font-weight: 600;
                color: #2c3e50;
                background-color: white;
                border: none;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-top: 15px; /* 与标题间距 */
            }

            /* 输入框:默认灰色边框，聚焦时蓝色高亮 */
            QLineEdit {
                font-size: 10pt;
                border: 1px solid #d0d6e0;
                border-radius: 4px;
                padding-left: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                outline: none;
                background-color: #f8fafc;
            }

            /* 按钮:蓝白渐变，hover/点击有反馈 */
            QPushButton {
                font-size: 10pt;
                font-weight: 500;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #1c6ea4);
            }
            QPushButton:pressed {
                background: #1c6ea4;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
            }

            /* 右侧标题:浅灰底色，突出文字 */
            QLabel#right_title {
                background-color: #eef2f7;
                padding: 5px 0;
                border-radius: 4px;
            }

            /* 菜单栏:浅灰背景，文字深色 */
            QMenuBar {
                background-color: #eef2f7;
                color: #2c3e50;
                font-size: 10pt;
            }
            QMenuBar::item {
                padding: 0 15px;
            }
            QMenuBar::item:selected {
                background-color: #d0d6e0;
                border-radius: 3px;
            }

            /* 状态栏:白色背景，文字灰色 */
            QStatusBar {
                background-color: white;
                color: #7f8c8d;
                font-size: 9pt;
            }
        """
        MainWindow.setStyleSheet(style)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        # 窗口标题:与需求文档对齐
        MainWindow.setWindowTitle(_translate("MainWindow", "船舶三维建模系统"))
        # 按钮文本
        self.btn_confirm.setText(_translate("MainWindow", "确定"))
        self.btn_reset.setText(_translate("MainWindow", "重置"))


# 测试代码(可直接运行查看效果)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())