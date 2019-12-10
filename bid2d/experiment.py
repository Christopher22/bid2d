from typing import Sequence, Any, Tuple
import itertools
from copy import deepcopy
from enum import Enum
import random

from psychopy import visual
from psychopy.hardware.keyboard import Keyboard

from bid2d.stimulus import Stimulus
from bid2d.util.fixation_cross import FixationCross
from bid2d.util.avatar import Avatar


class Experiment:
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
                if self == Experiment.Position.Above
                else stim_y - (stim_height / 2) - distance,
            )

        def __str__(self):
            return self.value

    def __init__(self, samples: Sequence[Stimulus]):
        self.samples = samples

    def run(self, win_size: Tuple[int, int]):
        trials = Experiment.generate_trials(
            self.samples,
            position=(Experiment.Position.Above, Experiment.Position.Below),
        )

        # Create the window and load all images into the buffer
        window = visual.Window(win_size, checkTiming=True)
        all((trial.load(window) for trial in trials))

        fixation_cross = FixationCross(-0.5, 0.5, -0.5, 0.5, window)
        avatar = Avatar(window)

        keyboard = Keyboard(waitForStart=False)
        for trial in trials:
            # Show the fixation cross
            fixation_cross.show(1)

            # Get the stimulus and set the position of the avatar
            stimulus = trial.load(window)
            avatar.pos = trial["position"].calculate_avatar_position(stimulus)

            for frame in itertools.count():
                for key in keyboard.getKeys(
                    ("up", "down"), waitRelease=False, clear=True
                ):
                    if key.name == "up":
                        avatar.up()
                    elif key.name == "down":
                        avatar.down()

                avatar.draw(window)
                trial.draw(window)
                window.flip()

    @staticmethod
    def generate_trials(
        stimuli: Sequence[Stimulus], seed: int = 42, **conditions: Sequence[Any]
    ) -> Sequence[Stimulus]:
        trials = []
        for stimulus, condition in itertools.product(stimuli, *conditions.values()):
            stimulus = deepcopy(stimulus)
            stimulus.update(
                {
                    key: value
                    for key, value in zip(
                        conditions.keys(),
                        [condition] if len(conditions) == 1 else iter(condition),
                    )
                }
            )
            trials.append(stimulus)

        random.shuffle(trials, random=random.Random(seed).random)
        return trials
