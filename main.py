# python built-in modules
import json
import pathlib
import os

# project modules
import assets.assets
import assets
import hud

# third party modules
import pyglet

# constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
MAIN_MENU, IN_GAME, PAUSE_MENU = range(3)
STORY_FILENAME = 'story.json'
SAVE_DIR = 'saves'


class Game(object):
    def __init__(self, width, height, caption="", resizeable=False):
        self.window = pyglet.window.Window(width, height, caption, resizeable)
        self.story = self.load_story()

        # set clear color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)

        # initiate phases
        self.phases = {
            MAIN_MENU: MainMenu(self),
            IN_GAME: InGame(self, self.story),
            PAUSE_MENU: PauseMenu(self, ),
        }

        # set current phase to main menu
        self.cur_phase = self.phases[MAIN_MENU]
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def new_game(self):
        del self.phases[IN_GAME]
        self.phases[IN_GAME] = InGame(self, self.story)
        self.change_phase(IN_GAME)

    def load_game(self, state):
        del self.phases[IN_GAME]
        self.phases[IN_GAME] = InGame(self, self.story, state=state)
        self.change_phase(IN_GAME)

    def change_phase(self, phase):
        self.window.pop_handlers()
        self.cur_phase = self.phases[phase]
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

    def load_story(self, name=STORY_FILENAME):
        story = None
        with open(name) as story_json:
            story = json.load(story_json)

        # add name to each state
        for key, value in story['states'].items():
            story['states'][key]['name'] = key

        return story

    def save_state(self, state, name='0'):
        # create save files directory if it doesn't exist
        pathlib.Path(SAVE_DIR).mkdir(exist_ok=True)

        with open(os.path.join(SAVE_DIR, name), 'w') as save_file:
            save_file.write(state.get('name'))

    def load_state(self, name='0'):
        with open(os.path.join(SAVE_DIR, name)) as save_file:
            return self.story['states'][save_file.readline()]

    def load_all_states(self):
        states = []
        for path in pathlib.Path(SAVE_DIR).iterdir():
            with path.open() as save_file:
                states.append(self.story['states'][save_file.readline()])
        return states

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
                       func=self.game.new_game))
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


class ActionNotFound(Exception):
    def __init__(self, action):
        self.action = action
        self.message = 'Action not found: {action}'
        super().__init__(self.message)


class InGame(Phase):
    def __init__(self, game, story, state=None):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects
        self.story = story

        # current progress of the user in the story
        if state is None:
            self.state = self.story['states'].get('entry')

        self.prompt = None
        self.actions = None

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
                            func=self.game.change_phase,
                            func_args=[PAUSE_MENU]))

        self.show_prompt()
        self.show_actions()

    def show_prompt(self):
        if self.prompt is None:
            self.prompt = hud.Prompt(self.state.get('prompt'),
                                     batch=self.batch)
        else:
            self.prompt.update(self.state.get('prompt'))

    def hide_prompt(self):
        del self.prompt

    def show_actions(self):
        if self.actions is not None:
            self.hide_actions()

        texts = self.state.get('actions')
        funcs = [self.get_next_state for _ in texts]
        funcs_args = [[text] for text in texts]

        self.actions = hud.ButtonArray(
            texts,
            funcs=funcs,
            funcs_args=funcs_args,
            font_name="Segoe UI Black",
            font_size=14,
            x=SCREEN_WIDTH // 2,
            y=100,
            spacing_x=170,
            width=150,
            color=(255, 255, 255, 255),
            bg_color=(239, 68, 68),
            batch=self.batch,
        )

    def hide_actions(self):
        del self.actions

    def get_next_state(self, action):
        next_state = self.story['states'].get(action)
        if next_state is None:
            raise ActionNotFound(action)
        self.state = next_state
        self.show_prompt()
        self.show_actions()

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)

        if self.actions is not None:
            self.actions.on_mouse_press(x, y, button, modifiers)


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
                            func=self.game.change_phase,
                            func_args=[IN_GAME]))
        self.clickables.append(
            hud.Button('RESUME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.change_phase,
                       func_args=[IN_GAME]))
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
                func=self.game.change_phase,
                func_args=[MAIN_MENU]))
        self.clickables.append(
            hud.Button('SAVE PROGRESS',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 400,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))
        self.clickables.append(
            hud.Button('SURRENDER',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 500,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch))
        self.clickables.append(
            hud.Button('EXIT GAME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 600,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=pyglet.app.exit)
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
