# python built-in modules
import json
import pathlib
import os

# project modules
import assets
import hud

# third party modules
import pyglet

# constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
MAIN_MENU, IN_GAME, PAUSE_MENU, SAVED_GAMES, END_GAME = range(5)
STORY_FILENAME = 'story.json'
SAVE_DIR = 'saves'


class Game(object):
    def __init__(self, width, height, caption="", resizeable=False):
        self.window = pyglet.window.Window(width, height, caption, resizeable)
        self.window.set_icon(assets.house_icon)
        self.story = self.load_story()

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

    def main_menu(self):
        # self.phases[MAIN_MENU].reset()
        self.phases[MAIN_MENU] = MainMenu(self)
        self.change_phase(MAIN_MENU)

    def end_game(self, heading, desc, background=None):
        self.phases[END_GAME] = EndGame(self, heading, desc, background)
        self.change_phase(END_GAME)

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

    def quicksave(self, destination):
        self.save_state('0')  # initiate save using slot 0

        # if player exits, quicksave
        if destination == PauseMenu.TO_EXIT:
            pyglet.app.exit()

        # if player returns to menu, quicksave
        self.main_menu()

    def surrender(self):
        surrender_state = {'heading': "SURRENDERED", 'desc': 'You have surrendered...', 'background': 'surrender.jpg'}
        self.end_game(surrender_state['heading'], surrender_state['desc'], surrender_state['background'])

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
            hud.Button('LOAD LAST SESSION',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 550,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if quicksave_exist else
                       (254, 226, 226),
                       batch=self.batch,
                       func=self.game.load_game if quicksave_exist else None,
                       func_args=['0']))

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
        self.mode = mode

        pyglet.text.Label('SAVED GAMES',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

        function = self.game.load_game if mode == SavedGames.LOAD else self.save_game
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
                func=self.game.main_menu))

        self.slot_labels = []

        slot1_state = self.game.load_state('1')
        slot1_enable = force_enable or slot1_state
        self.clickables.append(
            hud.Button('SLOT 1',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2 - 120,
                       y=SCREEN_HEIGHT - 200,
                       width=200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot1_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot1_enable else None,
                       func_args=['1']))

        self.slot_labels.append(
            pyglet.text.Label(slot1_state.get('name') if slot1_state else '',
                              batch=self.batch,
                              x=SCREEN_WIDTH // 2 + 20,
                              y=SCREEN_HEIGHT - 200,
                              anchor_y='center',
                              color=(0, 0, 0, 255)))
        slot2_state = self.game.load_state('2')
        slot2_enable = force_enable or slot2_state
        self.clickables.append(
            hud.Button('SLOT 2',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2 - 120,
                       y=SCREEN_HEIGHT - 300,
                       width=200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot2_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot2_enable else None,
                       func_args=['2']))
        self.slot_labels.append(
            pyglet.text.Label(slot2_state.get('name') if slot2_state else '',
                              batch=self.batch,
                              x=SCREEN_WIDTH // 2 + 20,
                              y=SCREEN_HEIGHT - 300,
                              anchor_y='center',
                              color=(0, 0, 0, 255)))
        slot3_state = self.game.load_state('3')
        slot3_enable = force_enable or slot3_state
        self.clickables.append(
            hud.Button('SLOT 3',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2 - 120,
                       y=SCREEN_HEIGHT - 400,
                       width=200,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68) if slot3_enable else
                       (254, 226, 226),
                       batch=self.batch,
                       func=function if slot3_enable else None,
                       func_args=['3']))
        self.slot_labels.append(
            pyglet.text.Label(slot3_state.get('name') if slot3_state else '',
                              batch=self.batch,
                              x=SCREEN_WIDTH // 2 + 20,
                              y=SCREEN_HEIGHT - 400,
                              anchor_y='center',
                              color=(0, 0, 0, 255)))

    def save_game(self, name):
        self.game.save_state(name)
        self.refresh()

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)

    def refresh(self):
        for index, label in enumerate(self.slot_labels):
            state = self.game.load_state(str(index + 1))
            label.text = state.get('name') if state else ''


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

        self.prompt = None
        self.actions = None
        self.background = None

        # current progress of the user in the story
        if state == 'surrender':
            self.surrender()
            return
        elif not state:
            self.state = self.story['states'].get('entry')
        else:
            self.state = state

        pyglet.text.Label('IN GAME',
                          color=(0, 0, 0, 255),
                          anchor_x='center',
                          x=SCREEN_WIDTH // 2,
                          y=SCREEN_HEIGHT - 100,
                          batch=self.batch)

        self.clickables.append(
            hud.ImageButton(assets.pause_icon,
                            SCREEN_WIDTH - 50,
                            SCREEN_HEIGHT - 50,
                            batch=self.batch,
                            func=self.game.change_phase,
                            func_args=[PAUSE_MENU]))

        self.update_background()
        self.show_prompt()
        self.show_actions()

    def show_prompt(self):
        self.hide_prompt()
        self.prompt = hud.Prompt(self.state.get('prompt'), batch=self.batch)

    def hide_prompt(self):
        del self.prompt
        self.prompt = None

    def show_actions(self):
        self.hide_actions()

        action_list = self.state.get('actions')

        if not action_list:
            return

        texts = [action["name"] for action in action_list]
        funcs = [self.get_next_state for _ in action_list]
        funcs_args = [[action["next_state"]] for action in action_list]

        self.actions = hud.ButtonArray(
            texts,
            funcs=funcs,
            funcs_args=funcs_args,
            font_name="Segoe UI Black",
            font_size=14,
            x=(SCREEN_WIDTH - 200) / len(texts) / 2 + 100,
            y=130,
            spacing_x=(SCREEN_WIDTH - 200) / len(texts) + 10,
            width=(SCREEN_WIDTH - 200) / len(texts),
            color=(255, 255, 255, 255),
            bg_color=(239, 68, 68),
            multiline=True,
            batch=self.batch,
        )

    def hide_actions(self):
        del self.actions
        self.actions = None

    def update_background(self):
        del self.background
        if not self.state.get('background'):
            self.background = None
            return

        self.background = pyglet.sprite.Sprite(
            assets.backgrounds[self.state['background']],
            x=SCREEN_WIDTH / 2,
            y=SCREEN_HEIGHT / 2)

    def get_next_state(self, action):
        next_state = self.story['states'].get(action)
        if next_state is None:
            raise ActionNotFound(action)
        if next_state.get('endgame'):
            self.game.end_game(next_state['heading'], next_state['desc'],
                               next_state.get('background'))
            return
        self.state = next_state
        self.update_background()
        self.show_prompt()
        self.show_actions()

    def on_draw(self):
        self.game.window.clear()
        if self.background:
            self.background.draw()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)

        if self.actions:
            self.actions.on_mouse_press(x, y, button, modifiers)


class EndGame(Phase):
    def __init__(self, game, heading, desc, background=None):
        super().__init__(game)
        self.batch = pyglet.graphics.Batch()
        self.clickables = []  # list of clickable objects

        self.heading = pyglet.text.Label(heading,
                                         font_name="Press Start",
                                         font_size=22,
                                         color=(0, 0, 0, 255),
                                         anchor_x='center',
                                         x=SCREEN_WIDTH // 2,
                                         y=SCREEN_HEIGHT - 200,
                                         batch=self.batch)
        self.prompt = hud.Prompt(desc, batch=self.batch)

        if background:
            self.background = pyglet.sprite.Sprite(
                assets.backgrounds[background],
                x=SCREEN_WIDTH / 2,
                y=SCREEN_HEIGHT / 2)

        self.clickables.append(
            hud.Button('MAIN MENU',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=100,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.quicksave,
                       func_args=[PauseMenu.TO_MENU]))

    def on_draw(self):
        self.game.window.clear()
        if self.background:
            self.background.draw()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for clickable in self.clickables:
            clickable.on_mouse_press(x, y, button, modifiers)


class PauseMenu(Phase):
    TO_EXIT, TO_MENU = range(2)

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
            hud.ImageButton(assets.pause_icon,
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
            hud.Button('MAIN MENU',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 300,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.quicksave,
                       func_args=[PauseMenu.TO_MENU]))
        self.clickables.append(
            hud.Button('SAVE PROGRESS',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 400,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.save_state_phase))
        self.clickables.append(
            hud.Button('SURRENDER',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 500,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.surrender))
        self.clickables.append(
            hud.Button('EXIT GAME',
                       font_name="Segoe UI Black",
                       font_size=14,
                       x=SCREEN_WIDTH // 2,
                       y=SCREEN_HEIGHT - 600,
                       color=(255, 255, 255, 255),
                       bg_color=(239, 68, 68),
                       batch=self.batch,
                       func=self.game.quicksave,
                       func_args=[
                           PauseMenu.TO_EXIT
                       ]))  # BUG: produces 'error in sys.excepthook'

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
