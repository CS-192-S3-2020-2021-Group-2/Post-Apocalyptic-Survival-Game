import math
from itertools import zip_longest

import pyglet
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
                 func_args=[],
                 func_kargs={},
                 order_start=0):
        self.items = []
        self.func = func
        self.func_args = func_args
        self.func_kargs = func_kargs
        self.group = pyglet.graphics.Group()
        self.background = pyglet.graphics.OrderedGroup(0 + order_start,
                                                       parent=self.group)
        self.foreground = pyglet.graphics.OrderedGroup(1 + order_start,
                                                       parent=self.group)

        self.bg = pyglet.shapes.Rectangle(x,
                                          y,
                                          0,
                                          0,
                                          color=bg_color,
                                          batch=batch,
                                          group=self.background)

        self.items.append(self.bg)
        self.label = pyglet.text.Label(
            text,
            font_name=font_name,
            font_size=font_size,
            x=x,
            y=y,
            color=color,
            anchor_x='center',
            anchor_y='center' if not multiline else 'top',
            align=align,
            multiline=multiline,
            width=width,
            batch=batch,
            group=self.foreground)
        self.items.append(self.label)

        if width is None:
            width = self.label.content_width + 40
        else:
            self.label.width = width - 40
        if height is None:
            height = self.label.content_height + 30

        self.bg.width = width
        self.bg.anchor_x = width / 2
        self.bg.height = height
        self.bg.anchor_y = (height / 2) if not multiline else (height - 15)

    def __del__(self):
        self.label.delete()
        self.bg.delete()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.func and self.bg.x - self.bg.anchor_x <= x <= self.bg.x + (self.bg.width - self.bg.anchor_x) and self.bg.y - self.bg.anchor_y <= y <= self.bg.y + (self.bg.height - self.bg.anchor_y):
            self.func(*self.func_args, **self.func_kargs)


class ImageButton(object):
    '''
    assumes img anchor is centered
    '''
    def __init__(self,
                 img,
                 x=0,
                 y=0,
                 batch=None,
                 group=None,
                 func=None,
                 func_args=[],
                 func_kargs={}):
        self.button_sprite = pyglet.sprite.Sprite(img,
                                                  x,
                                                  y,
                                                  batch=batch,
                                                  group=group)
        self.func = func
        self.func_args = func_args
        self.func_kargs = func_kargs

    def __del__(self):
        self.button_sprite.delete()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.func and self.button_sprite.x - self.button_sprite.width / 2 <= x <= self.button_sprite.x + self.button_sprite.width / 2 and self.button_sprite.y - self.button_sprite.height / 2 <= y <= self.button_sprite.y + self.button_sprite.height / 2:
            self.func(*self.func_args, **self.func_kargs)


class ButtonArray(object):
    def __init__(self,
                 texts,
                 funcs=[],
                 funcs_args=[],
                 funcs_kargs=[],
                 font_name=None,
                 font_size=None,
                 color=(255, 255, 255, 255),
                 bg_color=(0, 0, 0),
                 x=0,
                 y=0,
                 spacing_x=0,
                 spacing_y=0,
                 width=None,
                 height=None,
                 align='left',
                 multiline=False,
                 batch=None,
                 order_start=0):
        '''
        texts - iterable of text
        funcs - iterable of func
        func_arg - iterable of func_args
        func_karg - iterable of func_kargs
        x, y - position of the first button
        spacing_x - button spacing in x
        spacing_y - button spacing in y
        '''
        self.buttons = []
        for i, (text, func, func_args, func_kargs) in enumerate(
                zip_longest(texts, funcs, funcs_args, funcs_kargs)):
            self.buttons.append(
                Button(text,
                       font_name=font_name,
                       font_size=font_size,
                       color=color,
                       bg_color=bg_color,
                       x=x + spacing_x * i,
                       y=y - spacing_y * i,
                       width=width,
                       height=height,
                       align=align,
                       multiline=multiline,
                       batch=batch,
                       func=func,
                       func_args=func_args if func_args is not None else [],
                       func_kargs=func_kargs if func_kargs is not None else {},
                       order_start=order_start))

    def __del__(self):
        for button in self.buttons:
            del button

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            button.on_mouse_press(x, y, button, modifiers)


class Prompt(object):
    def __init__(self, text, batch=None, group=None):
        self.text = pyglet.text.Label(text,
                                      font_name="Segoe UI",
                                      font_size=16,
                                      color=(0, 0, 0, 255),
                                      x=SCREEN_WIDTH // 2,
                                      y=170,
                                      width=SCREEN_WIDTH - 200,
                                      anchor_x='center',
                                      anchor_y='bottom',
                                      multiline=True,
                                      batch=batch,
                                      group=group)

    def __del__(self):
        self.text.delete()

    def update(self, text):
        self.text.text = text
