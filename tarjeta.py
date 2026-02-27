from persistence.db import get_connection
from security.crypto import encrypt, decrypt

class tarjeta:
    def __init__(self, id_tarjeta: int, numeroTarjeta: str, banco: str, tipoTarjeta: str, id_user: str):
        self.id_tarjeta = id_tarjeta
        self.numeroTarjeta = numeroTarjeta
        self.banco = banco
        self.tipoTarjeta = tipoTarjeta
        self.id_user = id_user

    def insert_tarjeta(self, numeroTarjeta, banco, tipoTarjeta):
            connection = get_connection()
            cursor = connection.cursor()

            numeroTarjeta_encrypt = encrypt(numeroTarjeta)
            
            sql = "INSERT INTO tarjeta(numeroTarjeta, banco, tipoTarjeta,) VALUES(%s, %s, %s)"
            cursor.execute(sql, ( numeroTarjeta_encrypt, banco, tipoTarjeta))
            connection.commit()

            cursor.close()
            connection.close()

    def get_tarjeta():
         
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT id_tarjeta, numeroTarjeta, banco, tipotarjeta, id_user FROM tarjeta"
        cursor.execute(sql)
        row = cursor.fetchall()

        return [
             tarjeta(
                id_tarjeta=row['id_tarjeta'],
                numeroTarjeta = decrypt(row['numeroTarjeta']),
                banco=row['banco'],
                tipoTarjeta=(row['tipoTarjeta']),
                id_user=(row['id_user'])
            )
            for row in row
        ]