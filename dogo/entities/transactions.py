from datetime import datetime
from enums.transaction_type import TransactionType
from persistence.db import get_connection
import pymysql

class Transaction():

    def __init__(self, id: int, description: str, date: datetime, amount: float, transaction_type: TransactionType):
        self.id = id
        self.description = description
        self.date = date
        self.amount = amount
        self.transaction_type = transaction_type

    @staticmethod
    def save(description: str, amount: float, transaction_type: str, id_account: int) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "INSERT INTO transaction (description, date, amount, transaction_type, id_account) VALUES (%s, NOW(), %s, %s, %s)"
            cursor.execute(sql, (description, amount, transaction_type, id_account))
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving transaction: {ex}")
            return False

    @staticmethod
    def get_transactions_by_account(id_account: int) -> list:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, description, date, amount, transaction_type FROM transaction WHERE id_account = %s"
            cursor.execute(sql, (id_account,))
            rows = cursor.fetchall()

            cursor.close()
            connection.close()

            transactions = []
            for row in rows:
                t = Transaction(
                    row["id"],
                    row["description"],
                    row["date"],
                    row["amount"],
                    TransactionType[row["transaction_type"]]
                )
                transactions.append(t)

            return transactions
        except Exception as ex:
            print(f"Error getting transactions: {ex}")
            return []