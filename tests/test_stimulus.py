import unittest
from pathlib import Path

from bid2d.stimulus import Stimulus


class TestStimulus(unittest.TestCase):
    def test_loading(self):
        example_file = Path(__file__).parent / "example" / "samples.csv"
        examples = list(Stimulus.from_csv(example_file, delimiter=","))

        self.assertEqual(False, examples[0].should_approach)
        self.assertEqual("Red", examples[0].name)

        self.assertEqual(True, examples[1].should_approach)
        self.assertEqual("Green", examples[1].name)
