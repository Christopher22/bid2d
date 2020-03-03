import psychopy


class FixationPoint:
    def __init__(self, x, y, radius, window: psychopy.visual.Window):
        self._circle = psychopy.visual.Circle(window, radius=radius, edges=64)
        self._circle.units = "height"  # Otherwise, we draw a ellipse
        self._circle.pos = (x, y)
        self._circle.setColor((0, 0, 0), "rgb255")
        self._window = window

    def draw(self):
        self._circle.draw()

    def show(self, duration: float):
        fixation_frame_durations = int((1 / self._window.monitorFramePeriod) * duration)

        for _ in range(fixation_frame_durations):
            self.draw()
            self._window.flip()

    @staticmethod
    def create(window: psychopy.visual.Window, size: float = 0.01) -> "FixationPoint":
        return FixationPoint(0, 0, size, window)
