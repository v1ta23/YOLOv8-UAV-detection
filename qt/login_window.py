# -*- coding: utf-8 -*-
# file: login_window.py
# 简洁极简主义登录界面 - Minimalist & Clean Design
from PyQt5.QtWidgets import (QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, 
                             QHBoxLayout, QMessageBox, QGraphicsDropShadowEffect, 
                             QWidget, QFrame)
from PyQt5.QtGui import QColor, QFont, QPainter, QBrush, QPen, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF, QEasingCurve, QPoint, QSize
from database_manager import DatabaseManager

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Detection System")
        self.setFixedSize(400, 520)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # 确保窗口置顶
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;") # 显式透明
        
        self.db_manager = DatabaseManager()
        self.drag_position = None
        self.initUI()

    def paintEvent(self, event):
        """ 绘制干净的纯白卡片，带有细微的阴影 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景填充
        path = QPainterPath()
        rect = QRectF(10, 10, self.width()-20, self.height()-20) # 留出阴影空间
        path.addRoundedRect(rect, 16, 16)
        
        # 纯白背景
        painter.fillPath(path, QColor("#FFFFFF"))
        
        # 非常细的灰色边框，增加质感
        pen = QPen(QColor("#EAEAEA"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

    def initUI(self):
        try:
            # 整体布局
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(40, 50, 40, 40)
            main_layout.setSpacing(25)

            # 顶部操作栏 (关闭按钮)
            top_layout = QHBoxLayout()
            top_layout.addStretch()
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(30, 30)
            self.close_btn.setCursor(Qt.PointingHandCursor)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #999999;
                    border: none;
                    font-size: 24px;
                    font-family: Arial;
                    padding-bottom: 2px;
                }
                QPushButton:hover {
                    color: #333333;
                    background-color: #F5F5F7;
                    border-radius: 15px;
                }
            """)
            self.close_btn.clicked.connect(self.reject)
            top_layout.addWidget(self.close_btn)

            # Logo / 标题区域
            self.title_label = QLabel("欢迎回来")
            self.title_label.setAlignment(Qt.AlignLeft)
            self.title_label.setStyleSheet("""
                color: #1D1D1F; 
                font-size: 28px; 
                font-weight: 600; 
                font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei UI", "Segoe UI", Roboto, sans-serif;
                letter-spacing: -0.5px;
            """)
            
            self.subtitle_label = QLabel("请登录您的账号")
            self.subtitle_label.setAlignment(Qt.AlignLeft)
            self.subtitle_label.setStyleSheet("""
                color: #86868B;
                font-size: 15px;
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                margin-top: 5px;
            """)

            # 输入框样式 (极简线条风格，聚焦时变色)
            input_style = """
                QLineEdit {
                    border: 2px solid #F5F5F7;
                    border-radius: 12px;
                    padding: 14px 16px;
                    background-color: #F5F5F7;
                    color: #1D1D1F;
                    font-size: 15px;
                    font-weight: 400;
                    font-family: "Microsoft YaHei UI", sans-serif;
                }
                QLineEdit:focus {
                    background-color: #FFFFFF;
                    border: 2px solid #0071E3; /* Apple Blue */
                }
                QLineEdit::placeholder {
                    color: #8E8E93;
                }
            """

            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText("用户名")
            self.username_input.setStyleSheet(input_style)
            self.username_input.setMinimumHeight(48)

            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("密码")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setStyleSheet(input_style)
            self.password_input.setMinimumHeight(48)
            self.password_input.returnPressed.connect(self.handle_login)

            # 登录按钮 (Apple Blue 风格)
            self.login_btn = QPushButton("登 录")
            self.login_btn.setCursor(Qt.PointingHandCursor)
            self.login_btn.setMinimumHeight(48)
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0071E3;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 500;
                    font-family: "Microsoft YaHei UI", sans-serif;
                }
                QPushButton:hover {
                    background-color: #0077ED;
                }
                QPushButton:pressed {
                    background-color: #006EDB;
                }
            """)
            self.login_btn.clicked.connect(self.handle_login)

            # 底部区域 (注册链接)
            bottom_layout = QHBoxLayout()
            bottom_layout.addStretch()
            
            self.register_label = QLabel("还没有账号吗？")
            self.register_label.setStyleSheet("color: #86868B; font-size: 13px; font-family: 'Microsoft YaHei UI';")
            
            self.register_btn = QPushButton("我要马上注册")
            self.register_btn.setCursor(Qt.PointingHandCursor)
            self.register_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #0071E3;
                    border: none;
                    font-size: 13px;
                    font-weight: 500;
                    font-family: 'Microsoft YaHei UI';
                }
                QPushButton:hover {
                    color: #0077ED;
                    text-decoration: underline;
                }
            """)
            self.register_btn.clicked.connect(self.handle_register)
            
            bottom_layout.addWidget(self.register_label)
            bottom_layout.addWidget(self.register_btn)
            bottom_layout.addStretch()

            # 组装布局
            # 注意顺序：顶部按钮 -> 标题 -> 输入框 -> 按钮 -> 底部链接
            # 使用 addSpacing 调整垂直间距
            content_layout = QVBoxLayout()
            content_layout.setSpacing(15)
            
            content_layout.addWidget(self.title_label)
            content_layout.addWidget(self.subtitle_label)
            content_layout.addSpacing(15) # 标题和输入框间距
            content_layout.addWidget(self.username_input)
            content_layout.addWidget(self.password_input)
            content_layout.addSpacing(10) # 输入框和按钮间距
            content_layout.addWidget(self.login_btn)
            
            main_layout.addLayout(top_layout)
            main_layout.addLayout(content_layout)
            main_layout.addStretch()
            main_layout.addLayout(bottom_layout)

            # 全局阴影
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(30)
            shadow.setXOffset(0)
            shadow.setYOffset(10)
            shadow.setColor(QColor(0, 0, 0, 40))
            self.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"Login Window Init Error: {e}")
            import traceback; traceback.print_exc()

    def _show_message(self, title, text, icon_type="warning"):
        """显示带样式的消息框，避免透明背景导致的黑色弹窗问题"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        if icon_type == "warning":
            msg.setIcon(QMessageBox.Warning)
        elif icon_type == "info":
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setIcon(QMessageBox.Critical)
        # 应用样式修复黑色背景问题
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #1D1D1F;
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QMessageBox QPushButton {
                background-color: #0071E3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0077ED;
            }
        """)
        msg.exec_()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.shake_window()
            return

        success, msg = self.db_manager.validate_user(username, password)
        if success:
            self.accept()
        else:
            self._show_message("登录失败", msg, "warning")
            self.shake_window()

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self._show_message("提示", "请输入用户名和密码", "warning")
            return

        success, msg = self.db_manager.register_user(username, password)
        if success:
            self._show_message("注册成功", "账号已创建，请直接登录。", "info")
        else:
            self._show_message("注册失败", msg, "warning")

    def shake_window(self):
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        start_pos = self.pos()
        self.anim.setKeyValueAt(0, start_pos)
        self.anim.setKeyValueAt(0.2, start_pos + QPoint(5, 0))
        self.anim.setKeyValueAt(0.4, start_pos + QPoint(-5, 0))
        self.anim.setKeyValueAt(0.6, start_pos + QPoint(5, 0))
        self.anim.setKeyValueAt(0.8, start_pos + QPoint(-5, 0))
        self.anim.setKeyValueAt(1, start_pos)
        self.anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
