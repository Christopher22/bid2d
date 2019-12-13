from typing import Sequence, Any, Tuple
import itertools
from copy import deepcopy
from enum import Enum
import random

from psychopy import visual, data
from psychopy.visual.backends.pygletbackend import PygletBackend
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler, UP, DOWN
from psychopy.iohub.client import launchHubServer

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

    class Reaction(Enum):
        NoReaction = (0,)
        Up = (1,)
        Down = (2,)
        CorrectReaction = (3,)
        IncorrectReaction = 4

        def validate(
            self, position: "Experiment.Position", should_approach: bool
        ) -> "Experiment.Reaction":
            if self not in (Experiment.Reaction.Up, Experiment.Reaction.Down):
                raise ValueError("Invalid state")

            if should_approach:
                if (
                    self == Experiment.Reaction.Up
                    and position == Experiment.Position.Below
                ):
                    return Experiment.Reaction.CorrectReaction
                elif self == Experiment.Reaction.Down == Experiment.Position.Above:
                    return Experiment.Reaction.CorrectReaction
            else:
                if (
                    self == Experiment.Reaction.Up
                    and position == Experiment.Position.Above
                ):
                    return Experiment.Reaction.CorrectReaction
                elif (
                    self == Experiment.Reaction.Down
                    and position == Experiment.Position.Below
                ):
                    return Experiment.Reaction.CorrectReaction

            return Experiment.Reaction.IncorrectReaction

        def __bool__(self):
            if self == Experiment.Reaction.CorrectReaction:
                return True
            elif self == Experiment.Reaction.IncorrectReaction:
                return False
            else:
                raise ValueError("The correctness of the reaction is not determined.")

    def __init__(self, win_size: Tuple[int, int], samples: Sequence[Stimulus]):
        self.samples = samples
        self._window = visual.Window(win_size, checkTiming=True)

    def run(self, participant: str):
        io = launchHubServer(
            experiment_code="BodyImageDistortion", session_code=participant
        )

        trials = Experiment.generate_trials(
            self.samples,
            position=(Experiment.Position.Above, Experiment.Position.Below),
        )

        # Load all the visible stimuli into the graphic buffer
        all((trial.load(self._window) for trial in trials))
        fixation_cross = FixationCross(-0.5, 0.5, -0.5, 0.5, self._window)
        avatar = Avatar(self._window)

        # It would be nice to use Psychopys keyboard feature - but it does not support holding keys down.
        # Therefore, get deeper into the rabbits hole...
        # >> keyboard = Keyboard(waitForStart=False)
        keyboard = KeyStateHandler()
        self.get_raw_window().push_handlers(keyboard)

        # Create the trial handler for logging purposes
        trial_handler = data.TrialHandler(
            trialList=[dict(trial.plain_data()) for trial in trials],
            nReps=1,
            method="sequential",
            dataTypes=("reaction_frame", "correct_response"),
        )
        io.createTrialHandlerRecordTable(trial_handler)

        # Iterate through the trials
        for trial, trial_data in zip(trials, trial_handler):
            # Show the fixation cross
            fixation_cross.show(1)

            # Get the stimulus and set the position of the avatar
            stimulus = trial.load(self._window)
            avatar.pos = trial["position"].calculate_avatar_position(stimulus)

            should_approach = trial_data[Stimulus.SHOULD_APPROACH]

            # Present the frames one after another and wait for the user reaction
            reaction = Experiment.Reaction.NoReaction
            for frame in itertools.count():

                # Handle the reaction of the user
                if keyboard[UP]:
                    avatar.up()
                    if reaction == Experiment.Reaction.NoReaction:
                        reaction = Experiment.Reaction.Up
                elif keyboard[DOWN]:
                    avatar.down()
                    if reaction == Experiment.Reaction.NoReaction:
                        reaction = Experiment.Reaction.Down

                # Check and log the first reaction
                if reaction in (Experiment.Reaction.Up, Experiment.Reaction.Down):
                    reaction = reaction.validate(
                        should_approach=should_approach, position=trial_data["position"]
                    )
                    trial_handler.addData("reaction_frame", frame)
                    trial_handler.addData("correct_response", bool(reaction))

                # Check if this trial should end
                if (should_approach and avatar.is_overlapping(stimulus)) or (
                    not should_approach and not avatar.is_on_screen()
                ):
                    break

                # Draw end present the simuli
                trial.draw(self._window)
                avatar.draw(self._window)
                self._window.flip()

            io.addTrialHandlerRecord(trial_data)

        io.quit()

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
