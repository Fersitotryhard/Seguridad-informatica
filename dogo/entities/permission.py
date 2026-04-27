from persistence.db import get_connection
import pymysql
from enums.value_permissions import ValuePermissions

class Permissions():
    def __init__(self, id: int, value: ValuePermissions):
        self.id = id
        self.value = value

    def get_permissions_by_user_id(id_user: int) -> list:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT id, value FROM permission WHERE id_user = %s"
            cursor.execute(sql, (id_user,))

            rs = cursor.fetchall()

            cursor.close()
            connection.close()

            permissions = []

            for row in rs:
                permissions.append(Permissions(row["id"], ValuePermissions[row["value"]]))

            return permissions
        except Exception as ex:
            print(f"Error fetching permissions: {ex}")
            return []