# third party modules
import pyglet


class MainWindow(pyglet.window.Window):
    def __init__(self, width, height, caption="", resizeable=False):
        super().__init__(width, height, caption, resizeable)
        self.main_batch = pyglet.graphics.Batch()

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def on_draw(self):
        '''
        GUI updates here
        '''
        # self.clear()
        self.main_batch.draw()

    def update(self, dt):
        '''
        logic updates here
        '''
        pass

    def on_mouse_press(self, x, y, button, modifier):
        print("Mouse pressed:", x, y, button, modifier)


if __name__ == "__main__":
    window = MainWindow(1280,
                        720,
                        "Post-Apocalyptic Survival Game",
                        resizeable=False)
    pyglet.app.run()