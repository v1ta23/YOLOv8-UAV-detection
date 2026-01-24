# -*- coding: utf-8 -*-
# file: test_app.py
# 使用 pytest 和 pytest-qt 测试登录系统
import pytest
import os
import sys

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


# ============================================
# 数据库管理器测试
# ============================================
class TestDatabaseManager:
    """测试 DatabaseManager 类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """每个测试前创建临时数据库"""
        self.test_db = str(tmp_path / "test_users.db")
        self.db = DatabaseManager(db_name=self.test_db)
    
    def test_register_user_success(self):
        """测试成功注册用户"""
        success, msg = self.db.register_user("testuser", "password123")
        assert success is True
        assert "成功" in msg
    
    def test_register_user_empty_username(self):
        """测试空用户名注册"""
        success, msg = self.db.register_user("", "password123")
        assert success is False
        assert "不能为空" in msg
    
    def test_register_user_empty_password(self):
        """测试空密码注册"""
        success, msg = self.db.register_user("testuser", "")
        assert success is False
        assert "不能为空" in msg
    
    def test_register_user_short_password(self):
        """测试过短密码"""
        success, msg = self.db.register_user("testuser", "123")
        assert success is False
        assert "至少" in msg
    
    def test_register_duplicate_user(self):
        """测试重复注册用户"""
        self.db.register_user("duplicate", "password123")
        success, msg = self.db.register_user("duplicate", "password456")
        assert success is False
        assert "已存在" in msg
    
    def test_validate_user_success(self):
        """测试成功登录"""
        self.db.register_user("logintest", "mypassword")
        success, msg = self.db.validate_user("logintest", "mypassword")
        assert success is True
        assert "成功" in msg
    
    def test_validate_user_wrong_password(self):
        """测试错误密码登录"""
        self.db.register_user("wrongpwtest", "correctpw")
        success, msg = self.db.validate_user("wrongpwtest", "wrongpw")
        assert success is False
        assert "密码错误" in msg or "错误" in msg
    
    def test_validate_user_not_exist(self):
        """测试不存在的用户登录"""
        success, msg = self.db.validate_user("nonexistent", "anypassword")
        assert success is False
        assert "不存在" in msg


# ============================================
# 登录窗口 UI 测试 (需要 pytest-qt)
# ============================================
class TestLoginWindow:
    """测试 LoginWindow UI"""
    
    @pytest.fixture(autouse=True)
    def setup(self, qtbot, tmp_path):
        """设置测试环境"""
        # 使用临时数据库
        self.test_db = str(tmp_path / "test_login_users.db")
        
        # 导入并创建窗口
        from login_window import LoginWindow
        self.window = LoginWindow()
        # 替换数据库为测试数据库
        self.window.db_manager = DatabaseManager(db_name=self.test_db)
        qtbot.addWidget(self.window)
        self.qtbot = qtbot
    
    def test_window_title(self):
        """测试窗口标题"""
        assert "Drone" in self.window.windowTitle() or "Detection" in self.window.windowTitle()
    
    def test_window_size(self):
        """测试窗口尺寸"""
        assert self.window.width() == 400
        assert self.window.height() == 520
    
    def test_input_fields_exist(self):
        """测试输入框存在"""
        assert self.window.username_input is not None
        assert self.window.password_input is not None
    
    def test_buttons_exist(self):
        """测试按钮存在"""
        assert self.window.login_btn is not None
        assert self.window.register_btn is not None
        assert self.window.close_btn is not None
    
    def test_password_is_hidden(self):
        """测试密码输入框是隐藏模式"""
        from PyQt5.QtWidgets import QLineEdit
        assert self.window.password_input.echoMode() == QLineEdit.Password
    
    def test_empty_login_shakes_window(self):
        """测试空登录触发抖动（不崩溃）"""
        self.window.username_input.setText("")
        self.window.password_input.setText("")
        # 调用登录处理，不应崩溃
        self.window.handle_login()
        # 如果没抛异常就算通过
        assert True
    
    def test_register_then_login(self):
        """测试注册后登录流程"""
        # 注册
        self.window.username_input.setText("pytestuser")
        self.window.password_input.setText("pytestpassword")
        
        # 模拟注册（直接调用数据库）
        success, _ = self.window.db_manager.register_user("pytestuser", "pytestpassword")
        assert success is True
        
        # 验证登录
        success, _ = self.window.db_manager.validate_user("pytestuser", "pytestpassword")
        assert success is True


# ============================================
# 主窗口测试 (集成测试)
# ============================================
from ui_main_window import DroneDetectionApp

class TestMainWindow:
    """测试主窗口功能"""

    @pytest.fixture(autouse=True)
    def setup(self, qtbot):
        """初始化主窗口"""
        # 为了测试界面而不加载真实大模型，传入 model_path=None
        self.window = DroneDetectionApp(model_path=None, model_loaded_ok=False)
        self.window.show()
        qtbot.addWidget(self.window)
        self.qtbot = qtbot

    def test_profile_button_exists(self):
        """测试用户头像按钮是否存在"""
        assert hasattr(self.window, 'btn_user_profile')
        assert self.window.btn_user_profile is not None
        assert self.window.btn_user_profile.isVisible()

    def test_profile_button_icon_or_text(self):
        """测试按钮是否有图标或文字"""
        # 我们知道生成了图片，所以应该有图标
        # 但为了健壮性，我们可以检查 icon 是否非空，或者 text 是否为 "User"
        has_icon = not self.window.btn_user_profile.icon().isNull()
        has_text = self.window.btn_user_profile.text() == "User"
        assert has_icon or has_text

    def test_logout_dialog(self, monkeypatch):
        """测试退出登录逻辑 (使用 monkeypatch 模拟弹窗)"""
        # 模拟 QMessageBox.question 返回 Yes
        from PyQt5.QtWidgets import QMessageBox
        monkeypatch.setattr(QMessageBox, 'question', lambda *args: QMessageBox.Yes)
        
        # 监听窗口关闭事件
        with self.qtbot.waitSignal(self.window.objectNameChanged) if False else context_manager_placeholder(): # simply calling logout
             pass
        
        # 直接调用 logout 方法
        self.window.logout()
        # 检查窗口是否已关闭 (isVisible 应该为 False)
        assert not self.window.isVisible()

# 辅助上下文管理器占位符
class context_manager_placeholder:
    def __enter__(self): pass
    def __exit__(self, *args): pass

# ============================================
# 运行测试
# ============================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
