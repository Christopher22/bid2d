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
    arguments = parser.parse_args()

    # Load the stimuli from the provided CSV file
    stimuli = list(Stimulus.from_csv(arguments.samples))

    # Prepare the LabStreamingLayer streams
    logger = Logger()

    # Query information about the participant and start the experiment
    experiment = Experiment(stimuli, fullscreen=False, logger=logger)
    experiment.prepare()
    experiment.run()

    # Gently close the PsychoPy. Otherwise, i.e. the window on Windows may hang
    core.quit()


if __name__ == "__main__":
    main()
