import argparse

from bid2d.experiment import Experiment, Stimulus
from bid2d.participant import Participant


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "samples", type=str, help="The CSV file with the required samples."
    )
    arguments = parser.parse_args()

    stimuli = list(Stimulus.from_csv(arguments.samples))

    participant = Participant.from_user(**{"Is patient?": False})
    if participant is not None:
        experiment = Experiment(stimuli, fullscreen=False)
        experiment.run(participant)


if __name__ == "__main__":
    main()
