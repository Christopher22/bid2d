import argparse

from bid2d.experiment import Experiment, Stimulus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "samples", type=str, help="The CSV file with the required samples."
    )
    arguments = parser.parse_args()

    stimuli = list(Stimulus.from_csv(arguments.samples))
    experiment = Experiment(stimuli)
    experiment.run((800, 800))


if __name__ == "__main__":
    main()
