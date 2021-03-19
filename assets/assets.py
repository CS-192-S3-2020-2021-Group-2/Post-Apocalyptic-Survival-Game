import pyglet

### FONTS ###
# Add font directory; Enables pyglet to search fonts found in this directory
pyglet.font.add_directory("assets/fonts")

# Loading fonts
subFont = pyglet.font.load("Press Start")
buttonFont = pyglet.font.load("Segoe UI Black")

### IMAGE ASSETS ###
# Icons
pause_icon = pyglet.image.load('assets/icons/pause.png')

# center the anchor of all images
images = [
    pause_icon,
]
for image in images:
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2