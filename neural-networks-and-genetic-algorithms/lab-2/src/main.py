STUDENT_ID = 22520278

import shutil
import csv
from pathlib import Path

import numpy as np
from scipy.stats import ttest_ind
from matplotlib import pyplot as plt
from scipy.stats.distributions import t

import imageio

import de
from objectives import *
from de import DifferentialEvolutionExperimentState
from cem import CrossEntropyMethodExperimentState

assets_dirpath = Path(__file__).parent.parent / "assets"
graphs_dirpath = assets_dirpath / "graphs"
logs_dirpath = assets_dirpath / "logs"
comparisons_dirpath = assets_dirpath / "comparisons"
gifs_dirpath = assets_dirpath / "gifs"
shutil.rmtree(assets_dirpath, ignore_errors=True)
assets_dirpath.mkdir()
graphs_dirpath.mkdir()
logs_dirpath.mkdir()
comparisons_dirpath.mkdir()
gifs_dirpath.mkdir()

for fitness_fn_builder in (Sphere, Griewank, Rosenbrock, Rastrigin, Ackley):
    for max_evaluations, parameters_num in ((2_000, 2), (10_000, 10)):
        comparison_csvfile = open(
            comparisons_dirpath
            / f"objective={fitness_fn_builder.__name__}_d={parameters_num}.csv",
            "w",
        )
        comparison_csvwriter = csv.writer(comparison_csvfile)
        comparison_csvwriter.writerow(("N", "DE", "CEM", "p-value"))

        for population_size in (8, 16, 32, 64, 128):
            de_best_fitnesses = []
            cem_best_fitnesses = []
            de_evaluation_steps = None
            cem_evaluation_steps = None

            de_logfile = open(
                logs_dirpath
                / f"DE_objective={fitness_fn_builder.__name__}_N={population_size}_d={parameters_num}.log",
                "w",
            )
            cem_logfile = open(
                logs_dirpath
                / f"CEM_objective={fitness_fn_builder.__name__}_N={population_size}_d={parameters_num}.log",
                "w",
            )

            for random_seed in range(STUDENT_ID, STUDENT_ID + 10):
                de_experiment_state = DifferentialEvolutionExperimentState(
                    population_size=population_size,
                    parameters_num=parameters_num,
                    fitness_fn=fitness_fn_builder(),
                    crossover_probability=0.5,
                    scale_factor=0.7,
                    random_seed=random_seed,
                )

                de_experiment_state = de_experiment_state.initializes()
                while de_experiment_state.evaluations_count < max_evaluations:
                    de_experiment_state = (
                        de_experiment_state.mutates()
                        .crosses_over()
                        .evaluates()
                        .selects()
                    )

                if de_evaluation_steps is None:
                    de_evaluation_steps = de_experiment_state.evaluation_steps

                de_best_fitnesses.append(de_experiment_state.best_fitnesses)

                de_logfile.writelines(
                    (
                        "#" * 60,
                        f"\nObjective: {fitness_fn_builder.__name__}",
                        f"\nN: {population_size}",
                        f"\nd: {parameters_num}",
                        f"\nSeed: {random_seed}",
                        f"\nBest solution: {de_experiment_state.best_solution}",
                        f"\nBest fitness: {de_experiment_state.best_fitnesses[-1]}\n",
                    )
                )

                cem_experiment_state = CrossEntropyMethodExperimentState(
                    population_size=population_size,
                    parameters_num=parameters_num,
                    elites_size=population_size // 2,
                    fitness_fn=fitness_fn_builder(),
                    initialize_factor=0.7,
                    update_variance=0.02,
                    random_seed=random_seed,
                )

                cem_experiment_state = cem_experiment_state.initializes()
                while cem_experiment_state.evaluations_count < max_evaluations:
                    cem_experiment_state = (
                        cem_experiment_state.samples_population()
                        .evaluates()
                        .selects_elites()
                        .updates_sampling_parameters()
                    )

                if cem_evaluation_steps is None:
                    cem_evaluation_steps = cem_experiment_state.evaluation_steps

                cem_best_fitnesses.append(cem_experiment_state.best_fitnesses)

                cem_logfile.writelines(
                    (
                        "#" * 60,
                        f"\nObjective: {fitness_fn_builder.__name__}",
                        f"\nN: {population_size}",
                        f"\nd: {parameters_num}",
                        f"\nSeed: {random_seed}",
                        f"\nBest solution: {de_experiment_state.best_solution}",
                        f"\nBest fitness: {de_experiment_state.best_fitnesses[-1]}\n",
                    )
                )

            de_logfile.close()
            cem_logfile.close()

            assert de_evaluation_steps is not None
            assert cem_evaluation_steps is not None

            de_best_fitnesses = np.array(de_best_fitnesses)
            cem_best_fitnesses = np.array(cem_best_fitnesses)

            de_average = np.average(de_best_fitnesses, axis=0)
            de_error = np.std(de_best_fitnesses, axis=0)

            cem_average = np.average(cem_best_fitnesses, axis=0)
            cem_error = np.std(cem_best_fitnesses, axis=0)

            figure = plt.figure(figsize=(8, 6))
            ax = figure.add_subplot(1, 1, 1)

            ax.plot(de_evaluation_steps, de_average, label=f"DE-{population_size}")
            ax.fill_between(
                de_evaluation_steps,
                de_average - de_error,
                de_average + de_error,
                alpha=0.2,
            )

            ax.plot(cem_evaluation_steps, cem_average, label=f"CEM-{population_size}")
            ax.fill_between(
                cem_evaluation_steps,
                cem_average - cem_error,
                cem_average + cem_error,
                alpha=0.2,
            )

            ax.set_xlabel("Evaluation Steps")
            ax.set_ylabel("Best Fitness")
            ax.set_title(
                f"Objective: {fitness_fn_builder.__name__} | N: {population_size} | d: {parameters_num}"
            )
            ax.legend()
            ax.grid()

            filepath = (
                graphs_dirpath
                / f"objective={fitness_fn_builder.__name__}_N={population_size}_d={parameters_num}.png"
            )
            plt.savefig(filepath)
            plt.close()

            ttest_result = ttest_ind(
                de_best_fitnesses[:, -1], cem_best_fitnesses[:, -1], axis=0
            )

            comparison_csvwriter.writerow(
                (
                    population_size,
                    f"{np.round(de_average[-1], decimals=2)}±{np.round(de_error[-1], decimals=2)}",
                    f"{np.round(cem_average[-1], decimals=2)}±{np.round(cem_error[-1], decimals=2)}",
                    np.round(ttest_result.pvalue, decimals=3),  # type: ignore
                )
            )
        comparison_csvfile.close()

for fitness_fn_builder in (Sphere, Griewank, Rosenbrock, Rastrigin, Ackley):
    fitness_fn = fitness_fn_builder()

    x = np.linspace(
        fitness_fn.input_domain_lower_bound, fitness_fn.input_domain_upper_bound, 100
    )
    y = x
    X, Y = np.meshgrid(x, y)
    print(X.shape, Y.shape)
    X_flatten = X.reshape(100**2, copy=False)
    Y_flatten = Y.reshape(100**2, copy=False)
    XY_flatten = np.concat((X_flatten[:, np.newaxis], Y_flatten[:, np.newaxis]), axis=1)
    print(XY_flatten.shape)
    Z = np.apply_along_axis(fitness_fn, axis=1, arr=XY_flatten).reshape(
        (100, 100), copy=False
    )

    de_experiment_state = DifferentialEvolutionExperimentState(
        population_size=32,
        parameters_num=2,
        fitness_fn=fitness_fn,
        crossover_probability=0.5,
        scale_factor=0.7,
        random_seed=STUDENT_ID,
    ).initializes()

    gif_filename = f"DE_objective={fitness_fn_builder.__name__}"
    de_gif_frames_dir = gifs_dirpath / gif_filename
    de_gif_frames_dir.mkdir()
    current_generation = 0
    images = []
    while de_experiment_state.evaluations_count < 5_000:
        de_experiment_state = (
            de_experiment_state.mutates().crosses_over().evaluates().selects()
        )
        population = de_experiment_state.population
        figure = plt.figure(figsize=(8, 8))
        ax = figure.add_subplot(1, 1, 1)
        ax.contourf(X, Y, Z, levels=100, cmap="viridis")
        ax.scatter(
            population[:, 0],
            population[:, 1],
            c="red",
            label=f"Generation {current_generation}",
        )
        ax.scatter(
            *fitness_fn.global_opts,
            c="white",
            marker="*",
            s=100,
            label="Global Optimum",
        )
        ax.legend()
        ax.set_title("DE Optimization Progress")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        frame_filepath = de_gif_frames_dir / f"frame_{current_generation}.png"
        figure.savefig(frame_filepath)
        plt.close(fig=figure)
        images.append(imageio.imread(frame_filepath))
        current_generation += 1

    imageio.mimsave(gifs_dirpath / (gif_filename + ".gif"), images, duration=1.1)
    shutil.rmtree(de_gif_frames_dir)

    cem_experiment_state = CrossEntropyMethodExperimentState(
        population_size=32,
        parameters_num=2,
        elites_size=16,
        fitness_fn=fitness_fn,
        initialize_factor=0.7,
        update_variance=0.02,
        random_seed=STUDENT_ID,
    ).initializes()

    gif_filename = f"CEM_objective={fitness_fn_builder.__name__}"
    cem_gif_frames_dir = gifs_dirpath / gif_filename
    cem_gif_frames_dir.mkdir()
    current_generation = 0
    images = []
    while cem_experiment_state.evaluations_count < 5_000:
        cem_experiment_state = (
            cem_experiment_state.samples_population()
            .evaluates()
            .selects_elites()
            .updates_sampling_parameters()
        )
        population = cem_experiment_state.population
        figure = plt.figure(figsize=(8, 8))
        ax = figure.add_subplot(1, 1, 1)
        ax.contourf(X, Y, Z, levels=100, cmap="viridis")
        ax.scatter(
            population[:, 0],
            population[:, 1],
            c="red",
            label=f"Generation {current_generation}",
        )
        ax.scatter(
            *fitness_fn.global_opts,
            c="white",
            marker="*",
            s=100,
            label="Global Optimum",
        )
        ax.legend()
        ax.set_title("CEM Optimization Progress")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        frame_filepath = cem_gif_frames_dir / f"frame_{current_generation}.png"
        figure.savefig(frame_filepath)
        plt.close(fig=figure)
        images.append(imageio.imread(frame_filepath))
        current_generation += 1

    imageio.mimsave(gifs_dirpath / (gif_filename + ".gif"), images, duration=1.1)
    shutil.rmtree(cem_gif_frames_dir)
