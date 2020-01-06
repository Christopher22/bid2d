from enum import Enum

from bid2d.position import Position


class Reaction(Enum):
    NoReaction = 0
    Up = 1
    Down = 2
    CorrectReaction = 3
    IncorrectReaction = 4

    def validate(self, position: Position, should_approach: bool) -> "Reaction":
        if self not in (Reaction.Up, Reaction.Down):
            raise ValueError("Invalid state")

        if should_approach:
            if self == Reaction.Up and position == Position.Below:
                return Reaction.CorrectReaction
            elif self == Reaction.Down == Position.Above:
                return Reaction.CorrectReaction
        else:
            if self == Reaction.Up and position == Position.Above:
                return Reaction.CorrectReaction
            elif self == Reaction.Down and position == Position.Below:
                return Reaction.CorrectReaction

        return Reaction.IncorrectReaction

    def __bool__(self):
        if self == Reaction.CorrectReaction:
            return True
        elif self == Reaction.IncorrectReaction:
            return False
        else:
            raise ValueError("The correctness of the reaction is not determined.")
