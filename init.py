from json import loads, dumps

from src.main import HMGame

try:
    with open('saves/save') as file:
        progress = loads(file.read())
except FileNotFoundError:
    progress = None

game = HMGame()#progress)

new_save = game.start_game()
new_save = dumps(new_save)
with open('saves/save', mode='w') as file:
    file.write(new_save)
