from persistence.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from enums.profile import Profile
from flask_login import UserMixin
from entities.permission import Permissions

class User (UserMixin):
    def __init__(self, id: int, name:str, email:str, password:str, profile: Profile, permissions: list, is_acttive: bool):
        self.id= id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.permissions = permissions
        self.is_active = is_acttive
    
    @staticmethod
    def check_email_exists(email) -> bool:
        """
            Verifica si la cuenta de correo electrónico ya se encuentra registrada.

            Parameters:
                email (str): Correo electrónico a validar.

            Returns:
                bool: True si el correo ya se encunetra registrado; de lo contrario, False.
        """
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT email from user WHERE email = %s"
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

            # 1. Guarda el usuario
            sql = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, hash_password))
            
            # 2. Obtiene el id del usuario recién creado
            user_id = cursor.lastrowid

            # 3. Crea la cuenta bancaria automáticamente
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
                    user["is_active"],
                    permissions
                )

            return None
        except Exception as ex:
            print(f"Error login user:{ex}")
            return False

    @staticmethod    
    def get_by_id(id):
            try:
                connection = get_connection()
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                
                sql = "SELECT id, name, email, password FROM user WHERE id = %s"
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
                        permissions,
                        user["is_active"],
                    )   

                return None
            except Exception as ex:
                print(f"Error login user:{ex}")
                return False
            
            