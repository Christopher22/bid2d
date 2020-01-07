import argparse

from psychopy import core

from bid2d.experiment import Experiment, Stimulus
from bid2d.participant import Participant


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "samples", type=str, help="The CSV file with the required samples."
    )
    arguments = parser.parse_args()

    # Load the stimuli from the provided CSV file
    stimuli = list(Stimulus.from_csv(arguments.samples))

    # Query information about the participant and start the experiment
    participant = Participant.from_user(**{"Is patient?": False})
    if participant is not None:
        experiment = Experiment(stimuli, fullscreen=False)
        experiment.run(participant)

    # Gently close the PsychoPy. Otherwise, i.e. the window on Windows may hang
    core.quit()


if __name__ == "__main__":
    main()
