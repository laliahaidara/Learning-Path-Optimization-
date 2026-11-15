"""Data model: learning modules and the standardized result returned by every algorithm.

Notation used in the complexity comments of every file in this package:
    n = number of modules, T = time budget, w_i = time of module i, v_i = score of module i.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class LearningModule:
    """A learning object: costs `time` units and yields `score` points.

    Creating or reading a module is O(1) (three fixed fields).
    """
    name: str
    time: int
    score: int


@dataclass
class Result:
    """Common output of all algorithms (makes comparing and testing easy).

    Creating a Result is O(1); the list `indices` is stored by reference, not copied.
    """
    algorithm: str
    value: int
    indices: List[int] = field(default_factory=list)
    operations: int = 0  # elementary-operation counter (independent of the hardware)


def validate_instance(modules, budget):
    """Checks the model assumptions: integer times >= 1, scores >= 0, budget T >= 0.

    Complexity: best case Θ(1) (negative budget, or the first module is invalid),
    worst case Θ(n) (every module is checked). Space Θ(1).
    """
    if budget < 0:                              # O(1)
        raise ValueError("negative budget")
    for m in modules:                           # loop runs at most n times
        if m.time < 1 or m.score < 0:           # O(1) per module -> O(n) in total
            raise ValueError(f"invalid module: {m}")


def evaluate(modules, indices):
    """Returns (total_time, total_score) of a set of module indices.

    Complexity: Θ(k) time with k = len(indices) <= n (two passes of k O(1) steps). Space Θ(1).
    """
    total_time = sum(modules[i].time for i in indices)    # k additions -> Θ(k)
    total_score = sum(modules[i].score for i in indices)  # k additions -> Θ(k)
    return total_time, total_score                         # O(1)
