import itertools
import random
from copy import deepcopy
from typing import Sequence, Any, Tuple

from psychopy.preferences import prefs

# Install a global shutdown key
prefs.general["shutdownKey"] = "q"
from psychopy import visual, data
from psychopy.visual.backends.pygletbackend import PygletBackend
from pyglet.window import Window
from pyglet.window.key import KeyStateHandler, UP, DOWN
from psychopy.iohub.client import launchHubServer

from bid2d.participant import Participant
from bid2d.stimulus import Stimulus
from bid2d.position import Position
from bid2d.reaction import Reaction
from bid2d.util.fixation_cross import FixationCross
from bid2d.util.avatar import Avatar


class Experiment:
    EXPERIMENT_NAME = "BodyImageDistortion"

    RESULT_REACTION = "reaction_frame"
    RESULT_CORRECT = "correct_response"
    RESULT_DURATION = "duration"

    def __init__(
        self,
        samples: Sequence[Stimulus],
        win_size: Tuple[int, int] = (1024, 768),
        fullscreen: bool = True,
    ):
        self.samples = samples
        self._window = visual.Window(win_size, checkTiming=True, fullscr=fullscreen)

    def run(self, participant: Participant):
        io = launchHubServer(
            experiment_code=Experiment.EXPERIMENT_NAME,
            session_code=str(participant),
            datastore_name=Experiment.EXPERIMENT_NAME,
            session_info={
                "code": str(participant),
                "user_variables": dict(**participant),
            },
        )

        # Create the trials and load all the visible stimuli into the graphic buffer
        trials = Experiment.generate_trials(
            self.samples, position=(Position.Above, Position.Below)
        )
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
            trialList=[
                dict(
                    (
                        *trial.plain_data(),
                        (Experiment.RESULT_REACTION, -1),
                        (Experiment.RESULT_DURATION, -1),
                        (Experiment.RESULT_CORRECT, False),
                    )
                )
                for trial in trials
            ],
            nReps=1,
            method="sequential",
            dataTypes=(
                Experiment.RESULT_REACTION,
                Experiment.RESULT_DURATION,
                Experiment.RESULT_CORRECT,
            ),
        )
        io.createTrialHandlerRecordTable(trial_handler)

        # Iterate through the trials
        for trial, trial_data in zip(trials, trial_handler):
            # Show the fixation cross
            fixation_cross.show(1)

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
                    trial_data[Experiment.RESULT_REACTION] = frame
                    trial_data[Experiment.RESULT_CORRECT] = bool(reaction)

                # Check if this trial should end
                if (should_approach and avatar.is_overlapping(stimulus)) or (
                    not should_approach and not avatar.is_on_screen()
                ):
                    trial_data[Experiment.RESULT_DURATION] = (
                        frame - trial_data[Experiment.RESULT_REACTION]
                    )
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
