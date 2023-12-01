from json import loads, dumps

from cryptography.fernet import Fernet as Fock_u

from R_Game.config.config import non_specific_byte_string


def load():
    f = Fock_u(non_specific_byte_string)
    try:
        with open('saves/save') as file:
            raw_save = file.read().encode()
            # TODO: add ome ifs for good measure
            decrypted = f.decrypt(raw_save).decode()
            progress = loads(decrypted)
    except:  # ловлю всі ерори і мені похуй абсолютно
        progress = None

    return progress


def save(input_):
    f = Fock_u(non_specific_byte_string)
    try:
        new_save = dumps(input_).encode()
        with open('saves/save', mode='w') as file:
            encrypted = f.encrypt(new_save).decode()
            file.write(encrypted)
        return True
    except:  # все ще похуй
        return False