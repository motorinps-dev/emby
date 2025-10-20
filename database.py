"""
Модуль для работы с базой данных SQLite
Хранит информацию о пользователях Emby и времени их первого входа
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "emby_bot.db"):
        """Инициализация подключения к базе данных"""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Создает подключение к БД"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Создает таблицы в базе данных если они не существуют"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emby_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                emby_user_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_login_at TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                telegram_username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_group_id INTEGER UNIQUE NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ База данных инициализирована")
    
    def add_emby_user(self, username: str, emby_user_id: str) -> bool:
        """Добавляет пользователя Emby в базу данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO emby_users (username, emby_user_id) VALUES (?, ?)",
                (username, emby_user_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"✅ Пользователь {username} добавлен в БД")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Пользователь {username} уже существует в БД")
            return False
    
    def update_first_login(self, emby_user_id: str, first_login_time: datetime) -> bool:
        """Обновляет время первого входа пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE emby_users SET first_login_at = ? WHERE emby_user_id = ? AND first_login_at IS NULL",
                (first_login_time, emby_user_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()
            if updated:
                logger.info(f"✅ Обновлено время первого входа для пользователя {emby_user_id}")
            return updated
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении времени первого входа: {e}")
            return False
    
    def get_users_to_delete(self, days: int = 14) -> List[Tuple[str, str, datetime]]:
        """Получает список пользователей для удаления (прошло N дней после первого входа)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT username, emby_user_id, first_login_at
            FROM emby_users
            WHERE first_login_at IS NOT NULL
            AND first_login_at <= ?
            AND is_deleted = 0
            AND username LIKE 'user%'
        ''', (cutoff_date,))
        
        users = cursor.fetchall()
        conn.close()
        
        logger.info(f"📋 Найдено {len(users)} пользователей для удаления")
        return users
    
    def mark_user_as_deleted(self, emby_user_id: str) -> bool:
        """Отмечает пользователя как удаленного"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE emby_users SET is_deleted = 1 WHERE emby_user_id = ?",
                (emby_user_id,)
            )
            conn.commit()
            conn.close()
            logger.info(f"✅ Пользователь {emby_user_id} отмечен как удаленный")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при отметке пользователя как удаленного: {e}")
            return False
    
    def add_admin(self, telegram_id: int, telegram_username: Optional[str] = None) -> bool:
        """Добавляет администратора"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admins (telegram_id, telegram_username) VALUES (?, ?)",
                (telegram_id, telegram_username)
            )
            conn.commit()
            conn.close()
            logger.info(f"✅ Администратор {telegram_id} добавлен")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Администратор {telegram_id} уже существует")
            return False
    
    def remove_admin(self, telegram_id: int) -> bool:
        """Удаляет администратора"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            if deleted:
                logger.info(f"✅ Администратор {telegram_id} удален")
            return deleted
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении администратора: {e}")
            return False
    
    def is_admin(self, telegram_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
        is_admin = cursor.fetchone() is not None
        conn.close()
        return is_admin
    
    def get_all_admins(self) -> List[int]:
        """Получает список всех администраторов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM admins")
        admins = [row[0] for row in cursor.fetchall()]
        conn.close()
        return admins
    
    def add_admin_group(self, telegram_group_id: int) -> bool:
        """Добавляет группу администраторов"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admin_groups (telegram_group_id) VALUES (?)",
                (telegram_group_id,)
            )
            conn.commit()
            conn.close()
            logger.info(f"✅ Группа администраторов {telegram_group_id} добавлена")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Группа {telegram_group_id} уже существует")
            return False
    
    def remove_admin_group(self, telegram_group_id: int) -> bool:
        """Удаляет группу администраторов"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admin_groups WHERE telegram_group_id = ?", (telegram_group_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            if deleted:
                logger.info(f"✅ Группа администраторов {telegram_group_id} удалена")
            return deleted
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении группы: {e}")
            return False
    
    def get_all_admin_groups(self) -> List[int]:
        """Получает список всех групп администраторов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_group_id FROM admin_groups")
        groups = [row[0] for row in cursor.fetchall()]
        conn.close()
        return groups
    
    def get_all_users(self) -> List[Tuple[str, str, Optional[datetime], bool]]:
        """Получает список всех пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, emby_user_id, first_login_at, is_deleted
            FROM emby_users
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        conn.close()
        return users
