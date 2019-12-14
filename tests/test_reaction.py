import unittest
import itertools

from bid2d.reaction import Reaction
from bid2d.position import Position


class TestReaction(unittest.TestCase):
    def test_validate(self):
        correct_responses = (
            (Reaction.Down, Position.Above, True),
            (Reaction.Down, Position.Below, False),
            (Reaction.Up, Position.Above, False),
            (Reaction.Up, Position.Below, True),
        )

        # Ensure correctness of all possible combinations
        for combination in itertools.product(
            (Reaction.Down, Reaction.Up),
            (Position.Above, Position.Below),
            (True, False),
        ):
            result = combination[0].validate(combination[1], combination[2])
            if result == Reaction.CorrectReaction:
                self.assertIn(combination, correct_responses)
            elif result == Reaction.IncorrectReaction:
                self.assertNotIn(combination, correct_responses)
            else:
                raise ValueError("Invalid result type")


if __name__ == "__main__":
    unittest.main()
