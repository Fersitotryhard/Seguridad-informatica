# entities/user.py
from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from enums.profile import Profile
from flask_login import UserMixin
from entities.permission import Permissions

class User(UserMixin):
    def __init__(self, id: int, name: str, email: str, password: str, profile, is_active: bool, permissions: list):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.is_active = is_active
        self.permissions = permissions

    def is_active(self, is_active=None):
        """Indica si el usuario está activo. Requerido por Flask-Login."""
        if is_active is not None:
            self.is_active = is_active
        return self.is_active

    def has_permission(self, permission_value: str) -> bool:
        """Verifica si el usuario tiene un permiso específico."""
        return any(p.value.name == permission_value for p in self.permissions)

    def is_admin(self) -> bool:
        return self.profile == Profile.ADMIN.name or self.profile == Profile.ADMIN.value or self.profile == "ADMIN" or str(self.profile) == "1"

    @staticmethod
    def check_email_exists(email) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row is not None

    @staticmethod
    def save(name: str, email: str, password: str) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            hash_password = generate_password_hash(password)
            sql = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, hash_password))
            user_id = cursor.lastrowid
            import random
            number = f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            sql_account = "INSERT INTO account (number, creation_date, id_user) VALUES (%s, NOW(), %s)"
            cursor.execute(sql_account, (number, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving user: {ex}")
            return False

    @staticmethod
    def check_login(email, password):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and check_password_hash(user["password"], password):
                permissions = Permissions.get_permissions_by_user_id(user["id"])
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["profile"],
                    bool(user["is_active"]),
                    permissions
                )
            return None
        except Exception as ex:
            print(f"Error login user: {ex}")
            return None

    @staticmethod
    def get_by_id(id):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, password, profile, is_active FROM user WHERE id = %s"
            cursor.execute(sql, (id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                permissions = Permissions.get_permissions_by_user_id(user["id"])
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["profile"],
                    bool(user["is_active"]),
                    permissions
                )
            return None
        except Exception as ex:
            print(f"Error get_by_id: {ex}")
            return None

    @staticmethod
    def get_all():
        """Retorna todos los usuarios. Solo para administradores."""
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT id, name, email, profile, is_active FROM user ORDER BY name"
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as ex:
            print(f"Error get_all users: {ex}")
            return []

    @staticmethod
    def add_permission(id_user: int, permission_value: str) -> bool:
        """Agrega un permiso a un usuario. Solo para administradores."""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            # Evitar duplicados
            sql_check = "SELECT id FROM permission WHERE id_user = %s AND value = %s"
            cursor.execute(sql_check, (id_user, permission_value))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return False  # ya existe
            sql = "INSERT INTO permission (value, id_user) VALUES (%s, %s)"
            cursor.execute(sql, (permission_value, id_user))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error adding permission: {ex}")
            return False

    @staticmethod
    def remove_permission(id_user: int, permission_value: str) -> bool:
        """Elimina un permiso de un usuario."""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            sql = "DELETE FROM permission WHERE id_user = %s AND value = %s"
            cursor.execute(sql, (id_user, permission_value))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error removing permission: {ex}")
            return False