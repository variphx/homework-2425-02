from typing import Self

import numpy as np
from numpy import typing as npt
from numpy.random import RandomState

from objectives import FitnessFn


class DifferentialEvolutionExperimentState:
    def __init__(
        self,
        *,
        population_size: int,
        parameters_num: int,
        fitness_fn: FitnessFn,
        crossover_probability: float,
        scale_factor: float,
        random_seed: int,
    ) -> None:
        self._population_size = population_size
        self._parameters_num = parameters_num
        self._fitness_fn = fitness_fn
        self._crossover_probability = crossover_probability
        self._scale_factor = scale_factor
        self._random_state = RandomState(random_seed)
        self._evaluations_count = 0
        self._best_fitnesses: list[np.float64] = []
        self._evaluation_steps: list[int] = []

    def evaluates(self) -> Self:
        self._trial_population_fitnesses = np.apply_along_axis(
            self._fitness_fn, axis=1, arr=self._trial_population
        )
        self._evaluations_count += self._population_size

        self._best_fitnesses.append(
            np.amin(
                (
                    np.amin(self._population_fitnesses),
                    np.amin(self._trial_population_fitnesses),
                )
            )
        )
        self._evaluation_steps.append(self._evaluations_count)

        return self

    def initializes(self) -> Self:
        self._population = (
            self._random_state.random_sample(
                size=(self._population_size, self._parameters_num)
            )
            * (
                self._fitness_fn.input_domain_upper_bound
                - self._fitness_fn.input_domain_lower_bound
            )
            + self._fitness_fn.input_domain_lower_bound
        )

        self._population_fitnesses = np.apply_along_axis(
            self._fitness_fn, axis=1, arr=self._population
        )
        self._evaluations_count += self._population_size
        self._best_fitnesses.append((np.amin(self._population_fitnesses)))
        self._evaluation_steps.append(self._evaluations_count)

        return self

    def mutates(self) -> Self:
        indices = np.arange(0, self._population_size - 1)
        self._mutant_population = np.empty(
            (self._population_size, self._parameters_num), dtype=np.float64
        )
        for i in range(self._population.shape[0]):
            selected_indices: npt.NDArray[np.uint] = self._random_state.choice(
                indices, size=3, replace=False
            )
            selected_indices[selected_indices >= i] += 1
            selected_mutant_prototypes = self._population[selected_indices]
            self._mutant_population[i, :] = selected_mutant_prototypes[
                0
            ] + self._scale_factor * (
                selected_mutant_prototypes[1] - selected_mutant_prototypes[2]
            )
        return self

    def crosses_over(self) -> Self:
        self._trial_population = self._population.copy()
        for i in range(self._population_size):
            crossover_parameter_index = self._random_state.randint(
                0, self._parameters_num
            )
            self._trial_population[i, crossover_parameter_index] = (
                self._mutant_population[i, crossover_parameter_index]
            )

            crossover_probabilities_mask = (
                self._random_state.random_sample(size=(self._parameters_num))
                <= self._crossover_probability
            )
            self._trial_population[i, crossover_probabilities_mask] = (
                self._mutant_population[i, crossover_probabilities_mask]
            )
        return self

    def selects(self) -> Self:
        next_generation_selection_mask = (
            self._trial_population_fitnesses < self._population_fitnesses
        )
        self._population[next_generation_selection_mask, :] = self._trial_population[
            next_generation_selection_mask, :
        ]
        self._population_fitnesses[next_generation_selection_mask] = (
            self._trial_population_fitnesses[next_generation_selection_mask]
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
    def best_solution(self):
        return np.asarray(
            self._population[self._population_fitnesses.argmin()], dtype=np.float64
        )
