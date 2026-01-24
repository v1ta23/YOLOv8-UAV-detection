# -*- coding: utf-8 -*-
# file: database_manager.py
# 使用 Argon2id 算法进行密码哈希，增加 Pepper 以提高安全性
import sqlite3
import os
import hashlib
from argon2 import PasswordHasher, exceptions

# ============================================
# Pepper (胡椒粉) - 应用级密钥
# 注意：生产环境中应将此值存储在环境变量或安全配置文件中
# ============================================
PEPPER = "DroneDetection@SecretPepper#2026!"

class DatabaseManager:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        # Argon2id 哈希器 (使用推荐的安全参数)
        self.ph = PasswordHasher(
            time_cost=3,        # 迭代次数
            memory_cost=65536,  # 内存使用 (64 MB)
            parallelism=4,      # 并行度
            hash_len=32,        # 哈希长度
            salt_len=16         # 盐长度
        )
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _add_pepper(self, password):
        """将密码与 Pepper 结合"""
        # 使用 HMAC 风格组合: password + pepper
        return password + PEPPER

    def _hash_password(self, password):
        """使用 Argon2id 哈希密码"""
        peppered_password = self._add_pepper(password)
        return self.ph.hash(peppered_password)

    def _verify_password(self, password_hash, password):
        """验证密码是否匹配"""
        peppered_password = self._add_pepper(password)
        try:
            self.ph.verify(password_hash, peppered_password)
            return True
        except exceptions.VerifyMismatchError:
            return False
        except exceptions.InvalidHashError:
            # 兼容旧的 SHA256 哈希 (迁移期间)
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            return password_hash == old_hash

    def register_user(self, username, password):
        """注册新用户"""
        if not username or not password:
            return False, "用户名或密码不能为空"
        
        if len(password) < 4:
            return False, "密码长度至少4位"

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            password_hash = self._hash_password(password)
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
            return True, "注册成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, f"注册错误: {e}"
        finally:
            conn.close()

    def validate_user(self, username, password):
        """验证用户登录"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                stored_hash = result[0]
                if self._verify_password(stored_hash, password):
                    return True, "登录成功"
                else:
                    return False, "密码错误"
            else:
                return False, "用户名不存在"
        except Exception as e:
            return False, f"登录错误: {e}"
        finally:
            conn.close()
