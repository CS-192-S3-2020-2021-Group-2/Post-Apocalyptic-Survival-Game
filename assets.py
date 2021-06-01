import pathlib
import os

import pyglet

BACKGROUND_DIR = 'assets/backgrounds'

### FONTS ###
# Add font directory; Enables pyglet to search fonts found in this directory
pyglet.font.add_directory("assets/fonts")

# Loading fonts
subFont = pyglet.font.load("Press Start")
buttonFont = pyglet.font.load("Segoe UI Black")

### IMAGE ASSETS ###
# Icons
pause_icon = pyglet.image.load('assets/icons/pause.png')
house_icon = pyglet.image.load('assets/icons/house8bit.png')

# Backgrounds
backgrounds = {}
for path in pathlib.Path(BACKGROUND_DIR).iterdir():
    backgrounds[path.name] = pyglet.image.load(
        os.path.join(BACKGROUND_DIR, path.name))

# center the anchor of all images
images = [pause_icon, house_icon, *backgrounds.values()]
for image in images:
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2