import pyglet
import math
from pyglet import font

# Note that the font, font size, and positions of labels are still subject to change

# font.add_file('assets/DUMMY-FONT.ttf')
# new_font = font.load('DUMMY FONT', 16)

# Main Menu / PHASE 0
label_title_1 = pyglet.text.Label("",
                                  font_name='DUMMY FONT',
                                  font_size=30,
                                  anchor_x='center',
                                  x=640,
                                  y=480)
label_title_2 = pyglet.text.Label("",
                                  font_name='DUMMY FONT',
                                  font_size=22.5,
                                  anchor_x='center',
                                  x=640,
                                  y=445)
label_names = pyglet.text.Label("Menina · Villarante · Virtucio",
                                font_name='DUMMY FONT',
                                font_size=10,
                                anchor_x='center',
                                x=640,
                                y=407)

label_button = []
label_button.append(
    pyglet.text.Label("NEW GAME",
                      font_name='DUMMY FONT',
                      font_size=10,
                      anchor_x='center',
                      x=640,
                      y=407))
label_button.append(
    pyglet.text.Label("LOAD SAVED",
                      font_name='DUMMY FONT',
                      font_size=10,
                      anchor_x='center',
                      x=640,
                      y=407))
label_button.append(
    pyglet.text.Label("LOAD QUICKSAVE",
                      font_name='DUMMY FONT',
                      font_size=10,
                      anchor_x='center',
                      x=640,
                      y=407))

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
        pass


class Button(object):
    def __init__(self,
                 text='',
                 font_name=None,
                 font_size=None,
                 color=(255, 255, 255, 255),
                 bg_color=(0, 0, 0),
                 x=0,
                 y=0,
                 width=None,
                 height=None,
                 align='left',
                 multiline=False,
                 batch=None,
                 func=None):
        self.items = []
        self.func = func

        self.bg = pyglet.shapes.Rectangle(
            x,
            y,
            0,
            0,
            color=bg_color,
            batch=batch,
            group=pyglet.graphics.OrderedGroup(1))

        self.items.append(self.bg)
        self.label = pyglet.text.Label(text,
                                       font_name=font_name,
                                       font_size=font_size,
                                       x=x,
                                       y=y,
                                       color=color,
                                       anchor_x='center',
                                       anchor_y='center',
                                       align=align,
                                       multiline=multiline,
                                       batch=batch,
                                       group=pyglet.graphics.OrderedGroup(2))
        self.items.append(self.label)

        if width is None:
            width = self.label.content_width + 40
        if height is None:
            height = self.label.content_height + 30
        self.bg.width = width
        self.bg.height = height
        self.bg.anchor_x = width / 2
        self.bg.anchor_y = height / 2

    def on_mouse_press(self, x, y, button, modifiers):
        if self.func and self.bg.x - self.bg.width / 2 <= x <= self.bg.x + self.bg.width / 2 and self.bg.y - self.bg.height / 2 <= y <= self.bg.y + self.bg.height / 2:
            self.func()


class ImageButton(object):
    '''
    assumes img anchor is centered
    '''
    def __init__(self, img, x=0, y=0, batch=None, group=None, func=None):
        self.button_sprite = pyglet.sprite.Sprite(img,
                                                  x,
                                                  y,
                                                  batch=batch,
                                                  group=group)
        self.func = func

    def on_mouse_press(self, x, y, button, modifiers):
        if self.func and self.button_sprite.x - self.button_sprite.width / 2 <= x <= self.button_sprite.x + self.button_sprite.width / 2 and self.button_sprite.y - self.button_sprite.height / 2 <= y <= self.button_sprite.y + self.button_sprite.height / 2:
            self.func()