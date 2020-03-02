from enum import Enum

import pylsl


class Logger:
    class Event(Enum):
        ExperimentStarted = 0
        StimulusShown = 1
        CorrectUserAction = 2
        IncorrectUserAction = 3

    def __init__(self):
        self._stream_info = pylsl.stream_info(
            "AffectiveSimonTask2d", type=pylsl.cf_int32
        )
        self._stream = pylsl.stream_outlet(self._stream_info)
