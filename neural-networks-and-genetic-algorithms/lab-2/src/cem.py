from typing import Self

import numpy as np
from numpy import typing as npt
from numpy.random import RandomState

from objectives import FitnessFn


class CrossEntropyMethodExperimentState:
    def __init__(
        self,
        *,
        population_size: int,
        parameters_num: int,
        elites_size: int,
        initialize_factor: float,
        update_variance: float,
        fitness_fn: FitnessFn,
        random_seed: int,
    ) -> None:
        self._population_size = population_size
        self._parameters_num = parameters_num
        self._elites_size = elites_size
        self._initialize_factor = initialize_factor
        self._update_variance = update_variance
        self._fitness_fn = fitness_fn
        self._random_state = RandomState(random_seed)
        self._best_fitnesses: list[np.float64] = []
        self._evaluation_steps: list[int] = []
        self._evaluations_count = 0

    def evaluates(self) -> Self:
        self._population_fitnesses = np.apply_along_axis(
            self._fitness_fn, axis=1, arr=self._population
        )
        self._evaluations_count += self._population_size
        self._best_fitnesses.append((np.amin(self._population_fitnesses)))
        self._evaluation_steps.append(self._evaluations_count)
        return self

    def initializes(self) -> Self:
        self._sample_mean = (
            self._random_state.random_sample(self._parameters_num)
            * (
                self._fitness_fn.input_domain_upper_bound
                - self._fitness_fn.input_domain_lower_bound
            )
            + self._fitness_fn.input_domain_lower_bound
        ) / 2
        self._sample_covariance = self._initialize_factor * np.identity(
            self._parameters_num, dtype=np.float64
        )
        return self

    def samples_population(self) -> Self:
        self._population = self._random_state.multivariate_normal(
            mean=self._sample_mean,
            cov=self._sample_covariance,
            size=self._population_size,
        )
        return self

    def selects_elites(self) -> Self:
        elite_indices = np.argsort(self._population_fitnesses)[: self._elites_size]
        self._elites: npt.NDArray[np.float64] = self._population[elite_indices]
        return self

    def updates_sampling_parameters(self) -> Self:
        self._sample_mean = np.asarray(np.mean(self._elites, axis=0, dtype=np.float64))
        deviation = self._elites - self._sample_mean
        self._sample_covariance = (
            deviation.T @ deviation
        ) / self._elites_size + self._update_variance * np.identity(
            self._parameters_num, dtype=np.float64
        )
        return self

    @property
    def evaluations_count(self):
        return self._evaluations_count

    @property
    def best_fitnesses(self):
        return self._best_fitnesses

    @property
    def evaluation_steps(self):
        return self._evaluation_steps

    @property
    def population(self):
        return self._population

    @property
    def elites(self):
        return self._elites

    @property
    def best_solution(self):
        return self._elites[0, :]
