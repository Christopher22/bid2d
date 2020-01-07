from pathlib import Path
from typing import Union, Iterable, Mapping, Any
import argparse

from psychopy.iohub.datastore.util import ExperimentDataAccessUtility

from bid2d.experiment import Experiment
from bid2d.participant import Participant


class Analyzer:
    def __init__(self, data_file: str):
        self.file_path = Path(data_file)
        if not self.file_path.is_file():
            raise FileNotFoundError(data_file)
        self._file = None

    def __bool__(self):
        return self._file is not None

    def __enter__(self) -> "Analyzer":
        self._file = ExperimentDataAccessUtility(
            self.file_path.parent,
            self.file_path.name,
            experimentCode=Experiment.EXPERIMENT_NAME,
        )
        self._meta_data = self._file.getSessionMetaData()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def get_rows(
        self, participant: Union[Participant, str]
    ) -> Iterable[Mapping[str, Any]]:
        experiment_id = self._file._experimentID
        participant_uuid = (
            participant if isinstance(participant, str) else participant[Participant.ID]
        )
        participant_id = next(
            (
                participant.session_id
                for participant in self._meta_data
                if participant.user_variables[Participant.ID] == participant_uuid
            ),
            None,
        )

        # Load the dataset
        dataset = self._file.hdfFile.root["data_collection"]["condition_variables"][
            f"EXP_CV_{experiment_id}"
        ]
        if len(dataset) == 0:
            return

        column_indices = {name: i for i, name in enumerate(dataset[0].dtype.names)}
        for i in range(len(dataset)):
            row = dataset[i]

            # Skip non-matching rows
            if (
                row[column_indices["EXPERIMENT_ID"]] != experiment_id
                or row[column_indices["SESSION_ID"]] != participant_id
            ):
                continue

            yield {
                column: row[column_index]
                for column, column_index in column_indices.items()
                if column != "EXPERIMENT_ID" and column != "SESSION_ID"
            }

    @property
    def participants(self):
        if not self:
            raise ValueError("The experiment data is not opened.")

        for participant in self._meta_data:
            yield Participant(participant.user_variables)


if __name__ == "__main__":
    args = argparse.ArgumentParser("Analyzer")
    args.add_argument("path", help="Path to the HDF5 file", type=str)
    args.add_argument(
        "-participant", help="ID of the participant", default=None, type=str
    )

    args = args.parse_args()
    with Analyzer(args.path) as analyzer:
        if args.participant is None:
            print("\n".join(str(participant) for participant in analyzer.participants))
        else:
            for i, row in enumerate(analyzer.get_rows(args.participant)):
                # Print the column names
                if i == 0:
                    print("\t".join(row.keys()))

                # Print the row
                print(
                    "\t".join(
                        str(value)
                        if not value.dtype.kind == "S"
                        else "".join(chr(item) for item in value)
                        for value in row.values()
                    )
                )
