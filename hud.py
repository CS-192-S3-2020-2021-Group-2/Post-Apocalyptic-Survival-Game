import pyglet
import math
from pyglet import font

# constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

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
                 func=None,
                 order_start=0):
        self.items = []
        self.func = func
        self.background = pyglet.graphics.OrderedGroup(0 + order_start)
        self.foreground = pyglet.graphics.OrderedGroup(1 + order_start)

        self.bg = pyglet.shapes.Rectangle(x,
                                          y,
                                          0,
                                          0,
                                          color=bg_color,
                                          batch=batch,
                                          group=self.background)

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
                                       group=self.foreground)
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


class Prompt(object):
    def __init__(self, text, batch=None, group=None):
        self.text = pyglet.text.Label(text,
                                      font_name="Segoe UI",
                                      font_size=16,
                                      color=(0, 0, 0, 255),
                                      x=SCREEN_WIDTH // 2,
                                      y=100,
                                      width=SCREEN_WIDTH - 200,
                                      anchor_x='center',
                                      anchor_y='bottom',
                                      multiline=True,
                                      batch=batch,
                                      group=group)

    def update(self, text):
        self.text.text = text