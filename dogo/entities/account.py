from datetime import datetime
from entities.user import User
from persistence.db import get_connection
from entities.transactions import Transaction

import pymysql

class Account():

    def __init__(self, id: int, number: str, creation_date: datetime, user: User, transactions: list):
        self.id = id
        self.number = number
        self.creation_date = creation_date
        self.user = user
        self.transactions = transactions
    
    def get_account_by_user(id_user: int):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, number, creation_date FROM account WHERE id_user = %s"
            cursor.execute(sql, (id_user,))
            rs = cursor.fetchone()

            cursor.close()
            connection.close()

            user = User.get_by_id(id_user)
            transactions = Transaction.get_transactions_by_account(rs["id"])
            account = Account(
                rs["id"],
                rs["number"],
                rs["creation_date"],
                user,
                transactions
            )

            return account
        except Exception as ex:
            print(f"Error getting account by user:{ex}")
            return None
        

