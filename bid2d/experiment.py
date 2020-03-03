import itertools
import random
from copy import deepcopy
from typing import Sequence, Any, Tuple

from psychopy.preferences import prefs

# Install a global shutdown key
prefs.general["shutdownKey"] = "q"
from psychopy import visual
from psychopy.visual.backends.pygletbackend import PygletBackend
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler, UP, DOWN

from bid2d.stimulus import Stimulus
from bid2d.position import Position
from bid2d.reaction import Reaction
from bid2d.util.fixation_cross import FixationPoint
from bid2d.util.avatar import Avatar
from bid2d.logger import Logger


class Experiment:
    def __init__(
        self,
        samples: Sequence[Stimulus],
        logger: Logger,
        win_size: Tuple[int, int] = (1024, 768),
        fullscreen: bool = True,
    ):
        self.samples = samples
        self.logger = logger
        self._window = visual.Window(win_size, checkTiming=True, fullscr=fullscreen)

    def prepare(self):
        while not self.logger:
            self._window.flip()

    def run(
        self,
        fixation_cross_jitter: Tuple[float, float],
        seed: int,
        avatar_size: float,
        stimulus_size: float,
    ):
        # Create the trials and load all the visible stimuli into the graphic buffer
        trials = Experiment.generate_trials(
            self.samples, position=(Position.Above, Position.Below), seed=seed
        )
        all((trial.load(self._window, stimulus_size=stimulus_size) for trial in trials))
        fixation_cross = FixationPoint.create(self._window)
        avatar = Avatar(self._window, avatar_size=avatar_size)
        random_generator = random.Random(seed)

        # It would be nice to use Psychopys keyboard feature - but it does not support holding keys down.
        # Therefore, get deeper into the rabbits hole...
        # >> keyboard = Keyboard(waitForStart=False)
        keyboard = KeyStateHandler()
        self.get_raw_window().push_handlers(keyboard)

        # Iterate through the trials
        for trial in trials:
            # Show the fixation cross
            fixation_cross.show(random_generator.uniform(*fixation_cross_jitter))

            # Log the start of the trial
            self.logger.push(
                Logger.Trial(name=trial["name"], position=trial["position"])
            )

            # Get the stimulus and set the position of the avatar
            stimulus = trial.load(self._window)
            avatar.pos = trial["position"].calculate_avatar_position(stimulus)

            should_approach = trial[Stimulus.SHOULD_APPROACH]

            # Present the frames one after another and wait for the user reaction
            reaction = Reaction.NoReaction
            for frame in itertools.count():
                # Handle the reaction of the user
                if keyboard[UP]:
                    avatar.up()
                    if reaction == Reaction.NoReaction:
                        reaction = Reaction.Up
                elif keyboard[DOWN]:
                    avatar.down()
                    if reaction == Reaction.NoReaction:
                        reaction = Reaction.Down

                # Check and log the first reaction
                if reaction in (Reaction.Up, Reaction.Down):
                    reaction = reaction.validate(
                        should_approach=should_approach, position=trial["position"]
                    )
                    self.logger.push(
                        Logger.Reaction(
                            num_frames=frame,
                            correct_response=bool(reaction),
                            should_approach=should_approach,
                        )
                    )

                # Check if this trial should end
                if (should_approach and avatar.is_overlapping(stimulus)) or (
                    not should_approach and not avatar.is_on_screen()
                ):
                    self.logger.push(
                        Logger.Trial(name=trial["name"], position=trial["position"])
                    )
                    break

                # Draw end present the simuli
                trial.draw(self._window)
                avatar.draw(self._window)
                self._window.flip()

    def get_raw_window(self) -> Window:
        backend = self._window.backend
        if not isinstance(backend, PygletBackend):
            raise NotImplementedError(
                "The backend is not pyglet and therefore not supported"
            )
        return backend.winHandle

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
