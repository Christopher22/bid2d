from pathlib import Path

from psychopy import visual


class Avatar(visual.ImageStim):
    def __init__(self, window, **kwargs):
        path = Path(__file__).parents[1] / "assets" / "avatar.png"
        super().__init__(window, image=str(path), **kwargs)
        self.speed = 0.01

    def up(self):
        x, y = self.pos
        self.pos = x, y + self.speed

    def down(self):
        x, y = self.pos
        self.pos = x, y - self.speed
