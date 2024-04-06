from json import loads, dumps

from cryptography.fernet import Fernet as Fock_u

from R_Game.config.config import non_specific_byte_string


def load():
    f = Fock_u(non_specific_byte_string)
    try:
        with open('saves/save', 'r') as file:
            raw_save = file.read().encode()
            decrypted = f.decrypt(raw_save).decode()
            progress = loads(decrypted)
    except Exception as e:
        print(e)
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
    except Exception as e:
        print(e)
        return False


def encrypt_file(file_path):
    try:
        f = Fock_u(non_specific_byte_string)

        # open file for reading purpose
        fin = open(file_path, 'rb')

        # storing image data in variable "image"
        image = fin.read()
        fin.close()

        # converting image into byte array to perform decryption easily on numeric data
        image = bytes(image)

        image = f.encrypt(image)

        # opening file for writing purpose
        fin = open(file_path, 'wb')

        # writing decryption data in image
        fin.write(image)
        fin.close()
        print('Encryption Done...')
        return True

    except Exception as e:
        return False


def decrypt_file(file_path):
    try:
        f = Fock_u(non_specific_byte_string)

        # open file for reading purpose
        fin = open(file_path, 'rb')

        # storing image data in variable "image"
        image = fin.read()
        fin.close()

        # converting image into byte array to perform decryption easily on numeric data
        image = bytes(image)

        image = f.decrypt(image)

        # opening file for writing purpose
        fin = open(file_path, 'wb')

        # writing decryption data in image
        fin.write(image)
        fin.close()
        print('Decryption Done...')
        return True

    except Exception as e:
        return False

# encrypt_file('Pidorovich.png')
decrypt_file('Pidorovich.png')
