import joblib
import kagglehub
import pandas as pd
from typing import Literal
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans


def run():
    def rename_fn(name: str):
        return "_".join(name.strip().lower().split())

    def load_df(
        handle: str = "dev0914sharma/customer-clustering",
        path: str = "segmentation data.csv",
    ):
        df_filepath = kagglehub.dataset_download(
            handle=handle,
            path=path,
        )
        return pd.read_csv(df_filepath)

    df = load_df()
    df = df.drop(columns=["ID"]).rename(columns=rename_fn)

    columns_to_scale = ("age", "income")
    columns_to_encode = (
        "education",
        "marital_status",
        "occupation",
        "settlement_size",
        "sex",
    )

    def transform_df(
        df: pd.DataFrame,
        scalers: dict[Literal["age", "income"], StandardScaler],
        encoders: dict[
            Literal[
                "education", "marital_status", "occupation", "settlement_size", "sex"
            ],
            OneHotEncoder,
        ],
    ):
        for column in scalers.keys():
            df[column] = scalers[column].fit_transform(df[[column]])

        for column in encoders.keys():
            encoded = encoders[column].fit_transform(df[[column]])
            df_encoded = pd.DataFrame(
                encoded, columns=encoders[column].get_feature_names_out([column])
            )
            df = pd.concat((df.drop(columns=[column]), df_encoded), axis=1)

        return df, scalers, encoders

    scalers = dict((column, StandardScaler()) for column in columns_to_scale)
    encoders = dict(
        (column, OneHotEncoder(sparse_output=False)) for column in columns_to_encode
    )

    df, scalers, encoders = transform_df(df, scalers, encoders)
    joblib.dump(scalers, "assets/scalers.joblib")
    joblib.dump(encoders, "assets/encoders.joblib")
    joblib.dump(transform_df, "assets/transform_df.joblib")

    clusterer = KMeans(n_clusters=8).fit(df)
    joblib.dump(clusterer, "assets/kmeans.joblib")
