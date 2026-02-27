from entities.user import User
from getpass import getpass

def register_user():
    name = input("nombre: ")
    account = input("cuenta: ")

    if User.check_account_exists(account):
        print("La cuenta ya existe. Por favor, elige otra.")
        return

    password = input("contraseña: ")
    curp = getpass("CURP: ")
    
    User.insert(name, account, password, curp)


def view_user():
    users = User.get_users()

def login():
    account = input("cuenta: ")
    password = getpass("contraseña: ")

    user = User.get_user_by_account(account)
    if user and user.password == password:
        return True
    else:
        return False

if __name__ == "__main__":
    print("Inicio de sesión ")
    if login():
        print("Inicio de sesión exitoso")
    
        print("Seleccione una opción del menu: ")
        print("1. Registrar un usuario")
        print("2. Consultar Usuario")
        option = int(input())
        if option == 1:
            register_user()
        elif option == 2:
            view_user()
    else:
        print("Inicio de sesión fallido")    