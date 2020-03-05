from dataclasses import dataclass
from typing import Union, Iterable, Tuple

import numpy as np
import pylsl
from pyxdf import load_xdf

from bid2d.reaction import Position, Reaction


class Logger:
    TRIAL_STREAM_NAME = "AffectiveSimonTask2d_Trial"
    REACTION_STREAM_NAME = "AffectiveSimonTask2d_Reaction"

    @dataclass
    class Trial:
        name: str
        position: Position
        timestamp: float = 0.0

    @dataclass
    class Reaction:
        num_frames: int
        reaction: Reaction
        timestamp: float = 0.0

    def __init__(self):
        self._stream_trial = pylsl.stream_outlet(
            pylsl.stream_info(
                Logger.TRIAL_STREAM_NAME,
                channel_format=pylsl.cf_string,
                channel_count=2,
            )
        )
        self._stream_reaction = pylsl.stream_outlet(
            pylsl.stream_info(
                Logger.REACTION_STREAM_NAME,
                channel_format=pylsl.cf_int32,
                channel_count=2,
            )
        )

    def __bool__(self):
        return (
            self._stream_reaction.have_consumers()
            and self._stream_trial.have_consumers()
        )

    def push(self, event: Union["Trial", "Reaction"]):
        if isinstance(event, Logger.Trial):
            self._stream_trial.push_sample((event.name, event.position.value))
        elif isinstance(event, Logger.Reaction):
            self._stream_reaction.push_sample(
                (event.num_frames, int(event.reaction.value))
            )
        else:
            raise NotImplementedError("Unknown event!")

    @staticmethod
    def load_trials(file: str) -> Iterable["Trial"]:
        for timestamp, sample in Logger._load_stream(file, Logger.TRIAL_STREAM_NAME):
            yield Logger.Trial(name=sample[0], position=sample[1], timestamp=timestamp)

    @staticmethod
    def load_reactions(file: str) -> Iterable["Reaction"]:
        for timestamp, sample in Logger._load_stream(file, Logger.REACTION_STREAM_NAME):
            yield Logger.Reaction(
                num_frames=sample[0], reaction=Reaction(sample[1]), timestamp=timestamp,
            )

    @staticmethod
    def _load_stream(file: str, stream_name: str) -> Iterable[Tuple[float, np.ndarray]]:
        data, _meta = load_xdf(file)
        stream = next(
            (stream for stream in data if stream["info"]["name"] == [stream_name]), None
        )
        if stream is not None:
            for timestamp, sample in zip(stream["time_stamps"], stream["time_series"]):
                yield timestamp, sample


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("LoggerDecoder")
    parser.add_argument("file")

    args = parser.parse_args()
    for reaction in Logger.load_reactions(args.file):
        print(reaction)
