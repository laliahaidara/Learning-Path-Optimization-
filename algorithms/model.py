"""Data model: learning modules and the standardized result returned by every algorithm."""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class LearningModule:
    """A learning object: costs `time` units and yields `score` points."""
    name: str
    time: int
    score: int


@dataclass
class Result:
    """Common output of all algorithms (makes comparing and testing easy)."""
    algorithm: str
    value: int
    indices: List[int] = field(default_factory=list)
    operations: int = 0  # elementary-operation counter (independent of the hardware)


def validate_instance(modules, budget):
    """Checks the model assumptions: integer times >= 1, scores >= 0, budget T >= 0."""
    if budget < 0:
        raise ValueError("negative budget")
    for m in modules:
        if m.time < 1 or m.score < 0:
            raise ValueError(f"invalid module: {m}")


def evaluate(modules, indices):
    """Returns (total_time, total_score) of a set of module indices."""
    total_time = sum(modules[i].time for i in indices)
    total_score = sum(modules[i].score for i in indices)
    return total_time, total_score
