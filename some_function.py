from json import loads, dumps

from pathlib import Path

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


def encrypt_file(file_path, dest_path):
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
        fin = open(dest_path, 'wb')

        # writing decryption data in image
        fin.write(image)
        fin.close()
        print('Encryption Done...')
        return True

    except Exception as e:
        return False


def decrypt_file(file_path, dest_path):
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
        fin = open(dest_path, 'wb')

        # writing decryption data in image
        fin.write(image)
        fin.close()
        print('Decryption Done...')
        return True

    except Exception as e:
        return False


def get_files():
    source_dir = Path('R_Game/not cryptominer/homework/chat gpt killswitch')
    path_list = [
        ['R_Game/graphics/banners/Pidorovich.png', 'how_to_counter_ai'],
        ['R_Game/graphics/misc/radio.png', 'next_statement_is_false'],
        ['R_Game/audio/misc music/radio_music.mp3', 'previous_statement_is_true'],
        ['R_Game/audio/misc sounds/final_speech.mp3', 'thanks_for_listening_to_my_ted_talk']
    ]
    result = list()
    for index in range(4):
        file_path = Path(path_list[index][0])
        if not file_path.exists():
            decrypt_file(source_dir/path_list[index][1], file_path)
        result.append(file_path)
    return result
