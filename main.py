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
MAIN_MENU, IN_GAME, PAUSE_MENU, SAVED_GAMES = range(4)
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
            IN_GAME: InGame(self),
            PAUSE_MENU: PauseMenu(self)
        }

        # set current phase to main menu
        self.cur_phase = self.phases[MAIN_MENU]
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def get_ingame_state(self):
        return self.phases.get(IN_GAME).state

    def new_game(self):
        self.phases[IN_GAME] = InGame(self)
        self.change_phase(IN_GAME)

    def load_game(self, name='0'):
        self.phases[IN_GAME] = InGame(self, state=self.load_state(name))
        self.change_phase(IN_GAME)

    def save_state_phase(self):
        self.window.pop_handlers()
        self.cur_phase = SavedGames(self, SavedGames.SAVE)
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

    def load_state_phase(self):
        self.window.pop_handlers()
        self.cur_phase = SavedGames(self, SavedGames.LOAD)
        self.window.push_handlers(self.cur_phase.on_draw,
                                  self.cur_phase.on_key_press,
                                  self.cur_phase.on_mouse_press)

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

    def save_state(self, name='0'):
        state = self.get_ingame_state()
        # create save files directory if it doesn't exist
        pathlib.Path(SAVE_DIR).mkdir(exist_ok=True)

        with open(os.path.join(SAVE_DIR, name), 'w') as save_file:
            save_file.write(state.get('name'))

    def load_state(self, name='0'):
        path = os.path.join(SAVE_DIR, name)
        if not os.path.exists(path):
            return None
        with open(path) as save_file:
            return self.story['states'].get(save_file.readline())

    def slot_exists(self, name='0'):
        path = os.path.join(SAVE_DIR, name)
        return os.path.exists(path)

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
                       batch=self.batch,
                       func=self.game.load_state_phase))
        quicksave_exist = self.game.slot_exists('0')
        self.clickables.append(
            hud.Button('LOAD QUICKSAVE',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 550,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if quicksave_exist else
                       (254, 226, 226),
                       batch=self.batch,
                       func=self.game.load_game if quicksave_exist else None))

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)


class SavedGames(Phase):
    SAVE, LOAD = range(2)
    '''
    displays the saved games from previous sessions
    '''
    def __init__(self, game, mode):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects

        pyglet.text.Label('SAVED GAMES',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

        function = self.game.load_game if mode == SavedGames.LOAD else self.game.save_state
        force_enable = mode == SavedGames.SAVE

        self.clickables.append(
            hud.Button(
                'BACK',  # NOTE: Change to a 'Back' icon for distinguishability
                font_name="Segoe UI Black",
                font_size=14,
                x=SCREEN_WIDTH - 50,
                y=SCREEN_HEIGHT - 50,
                color=(0, 0, 0, 255),
                bg_color=(255, 255, 255),
                batch=self.batch,
                func=self.game.change_phase,
                func_args=[MAIN_MENU]))
        slot1_enable = force_enable or self.game.slot_exists('1')
        self.clickables.append(
            hud.Button('SLOT 1',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot1_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot1_enable else None,
                       func_args=['1']))
        slot2_enable = force_enable or self.game.slot_exists('2')
        self.clickables.append(
            hud.Button('SLOT 2',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 300,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot2_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot2_enable else None,
                       func_args=['2']))
        slot3_enable = force_enable or self.game.slot_exists('3')
        self.clickables.append(
            hud.Button('SLOT 3',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 400,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot3_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot3_enable else None,
                       func_args=['3']))

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
    def __init__(self, game, state=None):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects
        self.story = self.game.story

        # current progress of the user in the story
        if not state:
            self.state = self.story['states'].get('entry')
        else:
            self.state = state

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
        if not self.prompt:
            self.prompt = hud.Prompt(self.state.get('prompt'),
                                     batch=self.batch)
        else:
            self.prompt.update(self.state.get('prompt'))

    def hide_prompt(self):
        del self.prompt

    def show_actions(self):
        if not self.actions:
            self.hide_actions()

        actions = self.state.get('actions')
        texts = [action["name"] for action in actions]
        funcs = [self.get_next_state for _ in actions]
        funcs_args = [[action["next_state"]] for action in actions]

        self.actions = hud.ButtonArray(
            texts,
            funcs=funcs,
            funcs_args=funcs_args,
            font_name="Segoe UI Black",
            font_size=14,
            x=SCREEN_WIDTH // 2,
            y=100,
            spacing_x=170,
            # width=150,
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
            hud.Button(
                'SAVE PROGRESS',
                font_name="Segoe UI Black",
                font_size=14,
                x=SCREEN_WIDTH // 2,
                y=SCREEN_HEIGHT - 400,
                color=(255, 255, 255, 255),
                bg_color=(239, 68, 68),
                batch=self.batch,
                func=self.game.save_state_phase))
        self.clickables.append(
            hud.Button(
                'SURRENDER',  # non functional yet
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
