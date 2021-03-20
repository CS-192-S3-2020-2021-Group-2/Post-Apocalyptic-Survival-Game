# python built-in modules
import json
from enum import Enum

# project modules
import assets.assets
import assets
import hud

# third party modules
import pyglet

# constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
MAIN_MENU, IN_GAME, PAUSE_MENU = range(3)
STORY_PATH = 'story.json'


class Game(object):
    def __init__(self, width, height, caption="", resizeable=False):
        self.window = pyglet.window.Window(width, height, caption, resizeable)
        with open(STORY_PATH) as story_json:
            self.story = json.load(story_json)

        # set clear color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)

        # initiate phases
        self.phases = {
            MAIN_MENU: MainMenu(self),
            IN_GAME: InGame(self, self.story),
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
    '''
    handles main menu phase / screen
    '''
    def __init__(self, game):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects

        pyglet.text.Label("POST APOCALYPTIC SURVIVAL GAME",
                          font_name="Press Start",
                          font_size=22,
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 200,
                          batch=self.batch)
        pyglet.text.Label("MENINA · VILLARANTE · VIRTUCIO",
                          font_name="Press Start",
                          font_size=8,
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 250,
                          batch=self.batch)

        self.clickables.append(
            hud.Button('NEW GAME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 350,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=lambda: self.game.change_phase(IN_GAME)))
        self.clickables.append(
            hud.Button('LOAD SAVED',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 450,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))
        self.clickables.append(
            hud.Button('LOAD QUICKSAVE',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 550,
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
    def __init__(self, game, story):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects
        self.story = story
        self.state = self.story  # current progress of the user in the story
        self.prompt = None

        pyglet.text.Label('IN GAME',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

        self.clickables.append(
            hud.ImageButton(assets.assets.pause_icon,
                            SCREEN_WIDTH - 50,
                            SCREEN_HEIGHT - 50,
                            batch=self.batch,
                            func=lambda: self.game.change_phase(PAUSE_MENU)))

        self.show_prompt()

    def show_prompt(self):
        if self.prompt is None:
            self.prompt = hud.Prompt(self.state.get('prompt'),
                                     batch=self.batch)
        else:
            self.prompt.update(self.state.get('prompt'))

    def get_next_state(self, action):
        pass

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)


class PauseMenu(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects

        pyglet.text.Label('PAUSED',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

        self.clickables.append(
            hud.ImageButton(assets.assets.pause_icon,
                            SCREEN_WIDTH - 50,
                            SCREEN_HEIGHT - 50,
                            batch=self.batch,
                            func=lambda: self.game.change_phase(IN_GAME)))
        self.clickables.append(
            hud.Button('RESUME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=lambda: self.game.change_phase(IN_GAME)))
        self.clickables.append(
            hud.Button(
                'MAIN MENU',  # Changed "New Game" to "Main Menu"
                font_name="Segoe UI Black",
                font_size=14,
                x=SCREEN_WIDTH // 2,
                y=SCREEN_HEIGHT - 300,
                color=(255, 255, 255, 255),
                bg_color=(239, 68, 68),
                batch=self.batch,
                func=lambda: self.game.change_phase(MAIN_MENU)))
        self.clickables.append(
            hud.Button('SURRENDER',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 400,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))
        self.clickables.append(
            hud.Button('EXIT GAME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 500,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=lambda: pyglet.app.exit())
        )  # BUG: produces 'error in sys.excepthook'

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)


if __name__ == "__main__":
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT,
                  "Post-Apocalyptic Survival Game")
    pyglet.app.run()
