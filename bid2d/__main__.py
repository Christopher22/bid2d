import argparse

from psychopy import core

from bid2d.experiment import Experiment, Stimulus
from bid2d.logger import Logger


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "samples", type=str, help="The CSV file with the required samples."
    )
    parser.add_argument(
        "-avatar_size",
        type=float,
        help="The relative size of the avatar regarding its largest size.",
        default=0.4,
    )
    parser.add_argument(
        "-stimulus_size",
        type=float,
        help="The relative size of the stimulus regarding its largest size.",
        default=0.5,
    )
    parser.add_argument(
        "-seed", type=int, help="The seed for the random generator", default=42
    )
    parser.add_argument(
        "-fixation_jitter_min",
        type=float,
        help="Minimal duration of the fixation cross",
        default=0.75,
    )
    parser.add_argument(
        "-fixation_jitter_max",
        type=float,
        help="Maximal duration of the fixation cross",
        default=1.25,
    )
    parser.add_argument(
        "--no_fullscreen",
        dest="fullscreen",
        action="store_false",
        help="Do not start in fullscreen",
        default=True,
    )
    parser.add_argument(
        "--ignore_lsl",
        dest="prepare",
        action="store_false",
        help="Do not wait for a consumer for the Lab Streaming Layer streams",
        default=True,
    )

    arguments = parser.parse_args()

    # Load the stimuli from the provided CSV file
    stimuli = list(Stimulus.from_csv(arguments.samples))

    # Prepare the LabStreamingLayer streams
    logger = Logger()

    # Query information about the participant and start the experiment
    experiment = Experiment(stimuli, fullscreen=arguments.fullscreen, logger=logger)
    if arguments.prepare:
        experiment.prepare()
    experiment.run(
        seed=arguments.seed,
        fixation_cross_jitter=(
            arguments.fixation_jitter_min,
            arguments.fixation_jitter_max,
        ),
        avatar_size=arguments.avatar_size,
        stimulus_size=arguments.stimulus_size,
    )

    # Gently close the PsychoPy. Otherwise, i.e. the window on Windows may hang
    core.quit()


if __name__ == "__main__":
    main()
