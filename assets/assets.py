import pyglet

### FONTS ###
# Add font directory; Enables pyglet to search fonts found in this directory
pyglet.font.add_directory("fonts")

# Loading fonts
subFont = pyglet.font.load("Press Start")
buttonFont = pyglet.font.load("Segoe UI Black")

### IMAGE ASSETS ###