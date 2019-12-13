from pathlib import Path
from typing import Any, Iterable, Union, Tuple
import csv
from collections.abc import MutableMapping

from psychopy.visual import ImageStim, Window


class Stimulus(MutableMapping):
    NAME = "name"
    IMAGE_PATH = "image"
    SHOULD_APPROACH = "should_approach"

    def __init__(
        self, image: Union[str, Path], should_approach: bool, **extra_data: Any
    ):
        self.should_approach = should_approach
        self.extra_data = extra_data

        self._image = image if isinstance(image, Path) else Path(image)
        if not self._image.is_file():
            raise FileNotFoundError(f"Unable to find image '{self._image}'.")
        self.name = extra_data.pop(Stimulus.NAME, image.stem)

        self._loaded_image = None

    def __str__(self):
        return self.name

    def __bool__(self):
        return self.should_approach

    def __getitem__(self, k: str) -> Any:
        if k == Stimulus.NAME:
            return self.name
        elif k == Stimulus.SHOULD_APPROACH:
            return self.should_approach
        else:
            return self.extra_data[k]

    def __len__(self) -> int:
        return len(self.extra_data) + 2

    def __setitem__(self, k: str, v: Any) -> None:
        if k == Stimulus.NAME:
            self.name = v
        elif k == Stimulus.SHOULD_APPROACH:
            self.should_approach = v
        else:
            self.extra_data[k] = v

    def __delitem__(self, k: str) -> None:
        if k == Stimulus.NAME or k == Stimulus.SHOULD_APPROACH:
            raise ValueError("Not allowed to remove this key")
        del self.extra_data[k]

    def __iter__(self) -> Iterable[str]:
        yield Stimulus.NAME
        yield Stimulus.SHOULD_APPROACH
        yield from self.extra_data.keys()

    def load(self, window: Window, **kwargs) -> ImageStim:
        if self._loaded_image is None:
            self._loaded_image = ImageStim(window, image=str(self._image), **kwargs)
        return self._loaded_image

    def draw(self, win: Window, **kwargs):
        self.load(win, **kwargs).draw(win)

    @staticmethod
    def from_csv(
        asset_file: Union[Path, str], delimiter: str = ",", dialect: str = "excel"
    ) -> Iterable["Stimulus"]:
        asset_file = asset_file if isinstance(asset_file, Path) else Path(asset_file)
        with asset_file.open(mode="r", newline="") as csv_file:
            reader = csv.DictReader(csv_file, dialect=dialect, delimiter=delimiter)
            for sample in reader:
                path = (
                    Path(sample.pop(Stimulus.IMAGE_PATH))
                    if Stimulus.IMAGE_PATH in sample
                    else None
                )

                if path is None:
                    raise ValueError("Missing image path in CSV.")
                if not path.is_absolute():
                    sample[Stimulus.IMAGE_PATH] = Path(asset_file.parent, path)

                sample[Stimulus.SHOULD_APPROACH] = (
                    sample.pop(Stimulus.SHOULD_APPROACH).lower().strip() == "true"
                )
                yield Stimulus(**sample)

    def plain_data(self) -> Iterable[Tuple[str, Union[int, float, str, bool]]]:
        for key in self:
            value = self[key]
            yield key, str(value) if not isinstance(value, int) and not isinstance(
                value, float
            ) and not isinstance(value, bool) else value
