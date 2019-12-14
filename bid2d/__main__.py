import argparse

from bid2d.experiment import Experiment, Stimulus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "samples", type=str, help="The CSV file with the required samples."
    )
    arguments = parser.parse_args()

    stimuli = list(Stimulus.from_csv(arguments.samples))
    experiment = Experiment((800, 800), stimuli)
    experiment.run("TestParticipant")


if __name__ == "__main__":
    main()