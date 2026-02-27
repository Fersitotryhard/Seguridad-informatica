
from persistence.db import get_connection
from security.crypto import encrypt, decrypt 

class User:
    def __init__(self, id: int, name: str, account: str, password: str, curp: str):
        self.id = id
        self.name = name
        self.account = account
        self.password = password
        self.curp = curp

    def insert(self, name, account, password, curp):
            connection = get_connection()
            cursor = connection.cursor()

            password_encrypt = encrypt(password)
            curp_encrypt = encrypt(curp)
            
            sql = "INSERT INTO user(name, account, password, curp) VALUES(%s, %s, %s, %s)"
            cursor.execute(sql, (name, account, password_encrypt, curp_encrypt))
            connection.commit()

            cursor.close()
            connection.close()

    def check_account_exists(account):
        connection = get_connection()
        cursor = connection.cursor(dicctionary=True)

        sql = "SELECT account FROM user WHERE account = %s"
        cursor.execute(sql, (account,))  
        
        row = cursor.fetchone()

        if row is not None:
            return True
        else:
            return False

        return row is  None

        return cursor.fetchone() is None  
        

    def get_users():
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT id, name, account, password, curp FROM user"
        cursor.execute(sql)
        row = cursor.fetchall()

        return [
             User(
                id=row['id'],
                name=row['name'],
                account=row['account'],
                curp=decrypt(row['password']),
                password=decrypt(row['curp'])
            )
            for row in row
        ]
    def get_user_by_account(account):
         connection = get_connection()
         cursor = connection.cursor(dictionary=True)
         sql = "SELECT id, name, account, password, curp FROM user WHERE account = %s"

         cursor.execute(sql, (account,))
         row = cursor.fetchone()

         if row is None:
             return None
         else:
            return User(
                id=row['id'],
               name=row['name'],
                account=row['account'],
                curp=decrypt(row['password']),
                password=decrypt(row['curp'])
            )
