import pyglet
import math
from pyglet import font

# Note that the font, font size, and positions of labels are still subject to change

font.add_file('assets/DUMMY-FONT.ttf')
new_font = font.load('DUMMY FONT', 16)

# Main Menu / PHASE 0
label_title_1 = pyglet.text.Label("", font_name='DUMMY FONT', font_size=30, anchor_x='center', x=640, y=480)
label_title_2 = pyglet.text.Label("", font_name='DUMMY FONT', font_size=22.5, anchor_x='center', x=640, y=445)
label_names = pyglet.text.Label("Menina · Villarante · Virtucio", font_name='DUMMY FONT', font_size=10, anchor_x='center', x=640, y=407)

label_button = []
label_button.append(pyglet.text.Label("NEW GAME", font_name='DUMMY FONT', font_size=10, anchor_x='center', x=640, y=407))
label_button.append(pyglet.text.Label("LOAD SAVED", font_name='DUMMY FONT', font_size=10, anchor_x='center', x=640, y=407))
label_button.append(pyglet.text.Label("LOAD QUICKSAVE", font_name='DUMMY FONT', font_size=10, anchor_x='center', x=640, y=407))

# In Game / PHASE 1

# Pause Menu / PHASE 2



def draw(phase):
    if phase == 0:
        label_title_1.draw()
        label_title_2.draw()
        label_names.draw()

        for i in label_button:
            i.draw()
    
    elif phase == 2: