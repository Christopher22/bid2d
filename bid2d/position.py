from enum import Enum
from typing import Tuple

from psychopy import visual


class Position(Enum):
    Above = "above"
    Below = "below"

    def calculate_avatar_position(
        self, stimulus: visual.ImageStim
    ) -> Tuple[float, float]:
        stim_y = stimulus.pos[1]
        stim_height = stimulus.size[1]
        distance = (1 - (stim_y + (stim_height / 2))) / 2
        return (
            0.0,
            stim_y + (stim_height / 2) + distance
            if self == Position.Above
            else stim_y - (stim_height / 2) - distance,
        )

    def __str__(self):
        return self.value
