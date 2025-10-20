"""
Модуль для работы с Emby API
Предоставляет функции для управления пользователями и получения статистики
"""

import requests
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmbyAPI:
    def __init__(self, server_url: str, api_key: str):
        """
        Инициализация Emby API клиента
        
        Args:
            server_url: URL сервера Emby (например: http://localhost:8096)
            api_key: API ключ администратора Emby
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Создает нового пользователя в Emby
        
        Args:
            username: Имя пользователя (должно начинаться с "user")
            password: Пароль пользователя
        
        Returns:
            Словарь с данными пользователя или None в случае ошибки
        """
        try:
            url = f"{self.server_url}/emby/Users/New"
            data = {
                "Name": username,
                "Password": password
            }
            
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info(f"✅ Пользователь {username} создан в Emby, ID: {user_data.get('Id')}")
            return user_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при создании пользователя {username}: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Удаляет пользователя из Emby
        
        Args:
            user_id: ID пользователя в Emby
        
        Returns:
            True если удаление успешно, False в случае ошибки
        """
        try:
            url = f"{self.server_url}/emby/Users/{user_id}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Пользователь {user_id} удален из Emby")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при удалении пользователя {user_id}: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе по ID
        
        Args:
            user_id: ID пользователя в Emby
        
        Returns:
            Словарь с данными пользователя или None
        """
        try:
            url = f"{self.server_url}/emby/Users/{user_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при получении данных пользователя {user_id}: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Получает список всех пользователей Emby
        
        Returns:
            Список словарей с данными пользователей
        """
        try:
            url = f"{self.server_url}/emby/Users"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            users = response.json()
            logger.info(f"📋 Получено {len(users)} пользователей из Emby")
            return users
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при получении списка пользователей: {e}")
            return []
    
    def get_users_starting_with_user(self) -> List[Dict[str, Any]]:
        """
        Получает список пользователей, имена которых начинаются с "user"
        
        Returns:
            Список словарей с данными пользователей
        """
        all_users = self.get_all_users()
        user_users = [u for u in all_users if u.get('Name', '').startswith('user')]
        logger.info(f"📋 Найдено {len(user_users)} пользователей с именами, начинающимися на 'user'")
        return user_users
    
    def check_user_first_login(self, user_id: str) -> Optional[datetime]:
        """
        Проверяет время последней активности пользователя
        Если есть активность - это может быть первый вход
        
        Args:
            user_id: ID пользователя в Emby
        
        Returns:
            Datetime первого входа или None если пользователь не входил
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Проверяем LastActivityDate
            last_activity = user.get('LastActivityDate')
            if last_activity:
                # Формат: 2023-01-15T10:30:00.0000000Z
                login_time = datetime.strptime(last_activity[:19], "%Y-%m-%dT%H:%M:%S")
                logger.info(f"📅 Пользователь {user_id} последняя активность: {login_time}")
                return login_time
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке первого входа пользователя {user_id}: {e}")
            return None
    
    def get_user_playback_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Получает статистику просмотра пользователя
        
        Args:
            user_id: ID пользователя в Emby
        
        Returns:
            Словарь со статистикой просмотра
        """
        try:
            # Получаем последние воспроизведенные элементы
            url = f"{self.server_url}/emby/Users/{user_id}/Items"
            params = {
                'SortBy': 'DatePlayed',
                'SortOrder': 'Descending',
                'Filters': 'IsPlayed',
                'Recursive': 'true',
                'Limit': 50
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('Items', [])
            
            # Подсчитываем статистику
            stats = {
                'total_items_played': len(items),
                'movies': sum(1 for i in items if i.get('Type') == 'Movie'),
                'episodes': sum(1 for i in items if i.get('Type') == 'Episode'),
                'recent_items': []
            }
            
            # Добавляем последние просмотренные элементы
            for item in items[:10]:
                stats['recent_items'].append({
                    'name': item.get('Name'),
                    'type': item.get('Type'),
                    'played_date': item.get('UserData', {}).get('LastPlayedDate')
                })
            
            logger.info(f"📊 Статистика для пользователя {user_id}: {stats['total_items_played']} элементов")
            return stats
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при получении статистики пользователя {user_id}: {e}")
            return {
                'total_items_played': 0,
                'movies': 0,
                'episodes': 0,
                'recent_items': []
            }
    
    def update_user_policy(self, user_id: str, policy_updates: Dict[str, Any]) -> bool:
        """
        Обновляет политику пользователя (права доступа)
        
        Args:
            user_id: ID пользователя в Emby
            policy_updates: Словарь с обновлениями политики
        
        Returns:
            True если обновление успешно, False в случае ошибки
        """
        try:
            # Сначала получаем текущую политику
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            current_policy = user.get('Policy', {})
            
            # Обновляем политику
            current_policy.update(policy_updates)
            
            # Отправляем обновление
            url = f"{self.server_url}/emby/Users/{user_id}/Policy"
            response = requests.post(url, json=current_policy, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Политика пользователя {user_id} обновлена")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при обновлении политики пользователя {user_id}: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Тестирует подключение к Emby серверу
        
        Returns:
            True если подключение успешно, False в случае ошибки
        """
        try:
            url = f"{self.server_url}/emby/System/Info"
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            info = response.json()
            logger.info(f"✅ Подключение к Emby успешно: {info.get('ServerName')} v{info.get('Version')}")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка подключения к Emby: {e}")
            return False
