from cryptography.fernet import Fernet 

key = b'sqVL7Sp2hpdsFGr52DxoyeMcuPANgnMqZ_Bkusm666M='

fernet = Fernet(key)

def encrypt(value):
    return fernet.encrypt(value.encode()).decode()

def decrypt(value):
    return fernet.decrypt(value.encode()).decode()