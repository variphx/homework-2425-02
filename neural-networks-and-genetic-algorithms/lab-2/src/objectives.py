__all__ = ["Sphere", "Griewank", "Rosenbrock", "Rastrigin", "Ackley"]

from typing import Protocol

import numpy as np
from numpy import typing as npt


class FitnessFn(Protocol):
    input_domain_lower_bound: float
    input_domain_upper_bound: float
    global_opts: tuple[int, int]

    def __call__(self, individual: npt.ArrayLike) -> np.float64:
        raise NotImplementedError()


class Sphere(FitnessFn):
    input_domain_lower_bound: float = -5.12
    input_domain_upper_bound: float = 5.12
    global_opts: tuple[int, int] = (0, 0)

    def __call__(self, individual: npt.ArrayLike):
        individual = np.asarray(individual, dtype=np.float64)
        return np.sum(individual**2, dtype=np.float64)


class Griewank(FitnessFn):
    input_domain_lower_bound: float = -600.0
    input_domain_upper_bound: float = 600.0
    global_opts: tuple[int, int] = (0, 0)

    def __call__(self, individual: npt.ArrayLike):
        individual = np.asarray(individual, dtype=np.float64)

        a = np.sum(individual**2 / 4000)
        b_: npt.NDArray[np.float64] = np.cos(
            individual / np.sqrt(np.arange(1, individual.shape[0] + 1)),
            dtype=np.float64,
        )
        b = np.prod(b_, dtype=np.float64)

        return a - b + 1.0


class Rosenbrock(FitnessFn):
    input_domain_lower_bound: float = -5.0
    input_domain_upper_bound: float = 10.0
    global_opts: tuple[int, int] = (1, 1)

    def __call__(self, individual: npt.ArrayLike):
        individual = np.asarray(individual)
        excluded_last_individual_view = individual[:-1]
        excluded_first_individual_view = individual[1:]

        return np.sum(
            100.0
            * (excluded_first_individual_view - excluded_last_individual_view**2) ** 2
            + (excluded_last_individual_view - 1) ** 2,
            dtype=np.float64,
        )


class Rastrigin(FitnessFn):
    input_domain_lower_bound: float = -5.12
    input_domain_upper_bound: float = 5.12
    global_opts: tuple[int, int] = (0, 0)

    def __call__(self, individual: npt.ArrayLike):
        individual = np.asarray(individual)
        return (
            np.sum(
                individual**2 - 10.0 * np.cos(2.0 * np.pi * individual),
                dtype=np.float64,
            )
            + 10.0 * individual.shape[0]
        )


class Ackley(FitnessFn):
    input_domain_lower_bound: float = -32.768
    input_domain_upper_bound: float = 32.768
    global_opts: tuple[int, int] = (0, 0)
    a: int = 20
    b: float = 0.2
    c: float = 2 * np.pi

    def __call__(self, individual: npt.ArrayLike) -> np.float64:
        individual = np.asarray(individual)
        expop = np.exp
        sumop = np.sum

        return (
            -self.a
            * expop(np.sqrt(sumop(individual**2) / individual.shape[0]) * -self.b)
            - expop(sumop(np.cos(self.c * individual)) / individual.shape[0])
            + self.a
            + np.e
        )
