"""Instance generators (reproducible through a seed) for the experiments."""
import random

from algorithms import LearningModule

FAMILIES = ("uncorrelated", "weakly_correlated", "strongly_correlated")


def generate_instance(n, family, budget_ratio, seed, max_time=20):
    """Generates n modules and the budget T = budget_ratio · (sum of the times).

    uncorrelated: score independent of time.
    weakly_correlated: score = time ± small noise.
    strongly_correlated: score = time + constant (short modules have the best ratio).
    """
    rng = random.Random(seed)
    times = [rng.randint(1, max_time) for _ in range(n)]
    if family == "uncorrelated":
        scores = [rng.randint(1, max_time) for _ in times]
    elif family == "weakly_correlated":
        noise = max(1, max_time // 10)
        scores = [max(1, t + rng.randint(-noise, noise)) for t in times]
    elif family == "strongly_correlated":
        scores = [t + max_time // 2 for t in times]
    else:
        raise ValueError(f"unknown family: {family}")
    modules = [LearningModule(f"M{i + 1}", t, s) for i, (t, s) in enumerate(zip(times, scores))]
    return modules, max(1, int(budget_ratio * sum(times)))
