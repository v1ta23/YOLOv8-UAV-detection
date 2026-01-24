# -*- coding: utf-8 -*-
# file: main_app.py
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import Qt
# 从其他模块导入必要的类和函数
from ui_main_window import DroneDetectionApp
from utils import CustomSplashScreen

def run_application():
    """运行应用程序的主函数"""
    # --- 设置高 DPI 支持 ---
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # --- 创建和显示启动画面 ---
    try:
        # 尝试创建启动画面（如果需要）
        splash_pix = QPixmap(600, 300)
        splash_pix.fill(QColor(40, 44, 52)) # 深色背景
        painter = QPainter(splash_pix)
        painter.setPen(QColor(200, 200, 200))
        font = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(splash_pix.rect(), Qt.AlignCenter, "无人机检测系统\n正在启动...")
        painter.end()
        splash = CustomSplashScreen(splash_pix)
        splash.show()
        splash.setMessage("初始化...")
        app.processEvents() # 确保启动画面显示
    except Exception as e:
        print(f"创建启动画面时出错: {e}")
        splash = None # 出错则不使用启动画面

    # --- 模型相关变量 ---
    model_load_status = False
    model_file_path = None

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_relative_path = os.path.join('runs_ultralytics', 'uav_yolov8s_run', 'weights', 'best.pt')
        possible_paths = [
            os.path.join(script_dir, model_relative_path),
            os.path.join(script_dir, '..', model_relative_path),
        ]
        
        if splash:
            splash.setMessage("正在检查环境...")
            app.processEvents()

        for path in possible_paths:
            if os.path.exists(path):
                model_file_path = path
                model_load_status = True
                print(f"找到模型文件: {model_file_path}")
                break

        if splash:
            if model_load_status:
                splash.setMessage("模型加载成功")
            else:
                splash.setMessage(f"警告：未找到模型文件")
            app.processEvents()
            time.sleep(1) # 稍作停留让用户看清状态

    except Exception as e:
        print(f"初始化出错: {e}")
        if splash: splash.setMessage("初始化出错!")

    # --- 登录流程 ---
    from login_window import LoginWindow
    from PyQt5.QtWidgets import QDialog

    if splash:
        splash.setMessage("准备登录...")
        app.processEvents()
        time.sleep(0.5)
        splash.close() # 关闭启动画面

    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        # 登录成功，启动主程序
        try:
            mainWin = DroneDetectionApp(model_path=model_file_path, model_loaded_ok=model_load_status)
            mainWin.show()
            sys.exit(app.exec_())
        except Exception as e:
            print(f"创建主窗口时出错: {e}")
            QMessageBox.critical(None, "程序错误", f"无法初始化主窗口: {e}")
            sys.exit(1)
    else:
        # 登录取消或失败，退出程序
        sys.exit(0)

if __name__ == '__main__':
    run_application()