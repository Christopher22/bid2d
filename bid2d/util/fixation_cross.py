from typing import Optional
import psychopy.visual


class FixationCross:
    def __init__(self, x1, x2, y1, y2, window: psychopy.visual.Window):
        x_pos = x1 + ((x2 - x1) / 2)
        y_pos = y1 + ((y2 - y1) / 2)

        self._horizontal_line = psychopy.visual.Line(
            win=window, start=(x1, y_pos), end=(x2, y_pos)
        )
        self._vertical_line = psychopy.visual.Line(
            win=window, start=(x_pos, y1), end=(x_pos, y2)
        )
        self._window = window

    def draw(self):
        self._horizontal_line.draw()
        self._vertical_line.draw()

    def show(self, duration: float):
        fixation_frame_durations = int((1 / self._window.monitorFramePeriod) * duration)

        for _ in range(fixation_frame_durations):
            self.draw()
            self._window.flip()
