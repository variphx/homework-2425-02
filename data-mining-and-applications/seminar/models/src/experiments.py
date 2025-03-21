import kagglehub
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score


def load_df(
    handle: str = "dev0914sharma/customer-clustering",
    path: str = "segmentation data.csv",
):
    df_filepath = kagglehub.dataset_download(
        handle=handle,
        path=path,
    )
    return pd.read_csv(df_filepath)


def plot_dataset_distribution(df: pd.DataFrame, save_path_fmt: str):
    for column in df.columns:
        facet_grid = sns.displot(df, x=column)
        figure = facet_grid.figure
        figure.savefig(save_path_fmt.format(column), transparent=True)


columns_to_scale = ("Age", "Income")
columns_to_encode = (
    "Education",
    "Marital status",
    "Occupation",
    "Settlement size",
    "Sex",
)


def transform_df(
    df: pd.DataFrame,
    scalers: dict,
    encoders: dict,
    columns_to_scale=columns_to_scale,
    columns_to_encode=columns_to_encode,
):
    for column in columns_to_scale:
        df[column] = scalers[column].fit_transform(df[[column]])

    for column in columns_to_encode:
        encoded = encoders[column].fit_transform(df[[column]])
        df_encoded = pd.DataFrame(
            encoded, columns=encoders[column].get_feature_names_out([column])
        )
        df = pd.concat((df.drop(columns=[column]), df_encoded), axis=1)

    return df, scalers, encoders


def evaluate_cluster_model(
    clusterer,
    df: pd.DataFrame,
    min_n_clusters: int,
    max_n_clusters: int,
    model_name: str,
):
    distortions = []
    inertias = []
    silhouette_scores = []
    min_n_clusters = 2
    max_n_clusters = 64
    for n_clusters in range(min_n_clusters, max_n_clusters + 1):
        cluster_model = clusterer(n_clusters=n_clusters).fit(df)

        distortion = np.sum(
            np.square(
                np.min(
                    distance.cdist(df, cluster_model.cluster_centers_, "euclidean"),
                    axis=1,
                )
            )
        ) / len(df)
        distortions.append(distortion)

        inertia = cluster_model.inertia_
        inertias.append(inertia)

        sil_score = silhouette_score(df, cluster_model.predict(df))
        silhouette_scores.append(sil_score)

    for criterion, values, method in (
        ("distortion", distortions, "elbow-method"),
        ("inertia", inertias, "elbow-method"),
        ("silhouette", silhouette_scores, "scoring"),
    ):
        figure = plt.figure(figsize=(16, 8))
        ax = figure.add_subplot(1, 1, 1)
        ax.plot(
            np.arange(min_n_clusters, max_n_clusters + 1),
            values,
            "bx-",
            label=criterion,
        )
        ax.set_title(f"{method} using {criterion}")
        ax.set_xlabel("number of clusters")
        ax.set_ylabel(criterion)
        ax.grid()
        ax.legend()
        figure.savefig(
            f"assets/{model_name}-{method}-{criterion}.png",
            transparent=True,
        )


if __name__ == "__main__":
    df = load_df(
        handle="dev0914sharma/customer-clustering", path="segmentation data.csv"
    )

    plot_dataset_distribution(df, save_path_fmt="assets/data-distribution-{}.png")

    scalers = dict((column, StandardScaler()) for column in columns_to_scale)
    encoders = dict(
        (column, OneHotEncoder(sparse_output=False)) for column in columns_to_encode
    )

    df, _, _ = transform_df(df, scalers, encoders)

    evaluate_cluster_model(MiniBatchKMeans, df, 2, 64, model_name="MiniBatchKMeans")
