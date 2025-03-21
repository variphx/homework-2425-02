import joblib
import sqlite3
import kagglehub
import numpy as np
import pandas as pd
from typing import Literal
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, OneHotEncoder


con = sqlite3.connect("data-mining-and-application.seminar.db")


def rename_fn(name: str):
    return "_".join(name.strip().lower().split())


df = (
    pd.read_csv(
        kagglehub.dataset_download(
            handle="dev0914sharma/customer-clustering", path="segmentation data.csv"
        )
    )
    .drop(columns=["ID"])
    .rename(columns=rename_fn)
)


def transform_df(
    df: pd.DataFrame,
    scalers: dict[Literal["age", "income"], StandardScaler],
    encoders: dict[
        Literal["education", "marital_status", "occupation", "settlement_size", "sex"],
        OneHotEncoder,
    ],
):
    for column in scalers.keys():
        df[column] = scalers[column].transform(df[[column]])

    for column in encoders.keys():
        encoded = encoders[column].transform(df[[column]])
        df_encoded = pd.DataFrame(
            encoded, columns=encoders[column].get_feature_names_out([column])
        )
        df = pd.concat((df.drop(columns=[column]), df_encoded), axis=1)

    return df, scalers, encoders


scalers: dict[Literal["age", "income"], StandardScaler] = joblib.load(
    "assets/scalers.joblib"
)
encoders: dict[
    Literal["education", "marital_status", "occupation", "settlement_size", "sex"],
    OneHotEncoder,
] = joblib.load("assets/encoders.joblib")

transformed_df, _, _ = transform_df(df.copy(), scalers, encoders)

clusterer: KMeans = joblib.load("assets/kmeans.joblib")
y_pred = clusterer.predict(transformed_df)

pca = PCA(n_components=2)
decomposed_ndarray = pca.fit_transform(transformed_df)
decomposed_df = pd.DataFrame(data=decomposed_ndarray, columns=np.array(["x", "y"]))

joblib.dump(pca, "assets/pca.joblib")

df["cluster"] = y_pred
transformed_df["cluster"] = y_pred
decomposed_df["cluster"] = y_pred

cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS customers")
cur.execute("DROP TABLE IF EXISTS customers_transformed")
cur.execute("DROP TABLE IF EXISTS customers_decomposed")

df.to_sql(name="customers", con=con)
decomposed_df.to_sql(name="customers_decomposed", con=con)
transformed_df.to_sql(name="customers_transformed", con=con)
