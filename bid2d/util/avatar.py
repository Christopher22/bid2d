from pathlib import Path
from typing import Tuple

from psychopy import visual


class Avatar(visual.ImageStim):
    def __init__(self, window, avatar_size: float = 0.25, **kwargs):
        path = Path(__file__).parents[1] / "assets" / "avatar.png"
        super().__init__(window, image=str(path), **kwargs)
        self.speed = 0.01

        # Scale avatar relative to scene
        scale_factor = [value / max(self.size) for value in self.size]
        self.units = "norm"
        self.size = (avatar_size * scale_factor[0], avatar_size * scale_factor[1])

    def up(self):
        x, y = self.pos
        self.pos = x, y + self.speed

    def down(self):
        x, y = self.pos
        self.pos = x, y - self.speed

    def is_on_screen(self) -> bool:
        x, y = self.pos
        w, h = self.size
        return (
            x - w / 2 >= -1.0
            and x + w / 2 <= 1.0
            and y - h / 2 >= -1.0
            and y + h / 2 <= 1.0
        )

    def is_overlapping(self, stimulus: visual.ImageStim):
        x1, x2, y1, y2 = Avatar._calculate_rect(self)
        o_x1, o_x2, o_y1, o_y2 = Avatar._calculate_rect(stimulus)

        if x1 > o_x2 or o_x1 > x2:
            return False
        elif y1 < o_y2 or o_y1 < y2:
            return False
        else:
            return True

    @staticmethod
    def _calculate_rect(
        stimulus: visual.ImageStim
    ) -> Tuple[float, float, float, float]:
        x, y = stimulus.pos
        w, h = stimulus.size
        return x - w / 2, x + w / 2, y + h / 2, y - h / 2
