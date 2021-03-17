from enum import Enum

# project modules
import hud

# third party modules
import pyglet

# constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
MAIN_MENU, IN_GAME, PAUSE_MENU = range(3)


class Game(object):
    def __init__(self, width, height, caption="", resizeable=False):
        self.window = pyglet.window.Window(width, height, caption, resizeable)

        # set clear color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)

        # initiate phases
        self.phases = {
            MAIN_MENU: MainMenu(self),
            IN_GAME: InGame(self),
            PAUSE_MENU: PauseMenu(self),
        }

        # set current phase to main menu
        self.cur_phase = self.phases[MAIN_MENU]
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def change_phase(self, phase):
        self.window.pop_handlers()
        self.cur_phase = self.phases[phase]
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

    def update(self, dt):
        self.cur_phase.update(dt)


class Phase(object):
    '''
    abstract class
    '''
    def __init__(self, game):
        self.game = game

    def on_draw(self):
        pass

    def on_key_press(self, symbol, modifiers):
        print(symbol, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def update(self, dt):
        pass

    def reset(self):
        pass


class MainMenu(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects

        pyglet.text.Label("Menina · Villarante · Virtucio",
                          font_name='DUMMY FONT',
                          font_size=10,
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=200,
                          batch=self.batch)
        self.clickables.append(
            hud.Button('NEW GAME',
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 100,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=lambda: self.game.change_phase(IN_GAME)))
        self.clickables.append(
            hud.Button('LOAD SAVED',
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))
        self.clickables.append(
            hud.Button('LOAD QUICKSAVE',
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 300,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)


class InGame(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()

        pyglet.text.Label('IN GAME',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()


class PauseMenu(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()

        pyglet.text.Label('PAUSED',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)


if __name__ == "__main__":
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT,
                  "Post-Apocalyptic Survival Game")
    pyglet.app.run()