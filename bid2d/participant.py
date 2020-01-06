import uuid
from collections.abc import MutableMapping
from typing import Mapping, Any, Optional

from psychopy import gui


class Participant(MutableMapping):
    ID = "Id"

    def __init__(self, user_info: Mapping[str, Any]):
        self._data = dict(**user_info)
        if Participant.ID not in self._data:
            self._data[Participant.ID] = Participant.generate_id()

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        if key == Participant.ID and value != self._data[Participant.ID]:
            raise ValueError("It is not allowed to change the ID of the participant!")
        self._data[key] = value

    def __delitem__(self, key: str):
        if key == Participant.ID:
            raise ValueError("It is not allowed to delete the ID of the participant!")
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __str__(self):
        return self._data[Participant.ID]

    @staticmethod
    def from_user(**user_info: Any) -> Optional["Participant"]:
        participant = Participant(user_info)
        result = gui.DlgFromDict(
            participant,
            title="Participant",
            fixed=(Participant.ID,),
            copyDict=False,
            show=True,
        )
        return participant if result.OK else None

    @staticmethod
    def generate_id() -> str:
        id = uuid.uuid4()
        return str(id)
