import sqlite3
import joblib
import numpy as np
import pandas as pd
from typing import Literal
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_methods=["*"], allow_origins=["*"], allow_headers=["*"]
)

con = sqlite3.connect("data-mining-and-application.seminar.db")


class DashboardGetResponse(BaseModel):
    class Data(BaseModel):
        class Dataset(BaseModel):
            label: str
            data: list[float] | list[tuple[float, float]]

        labels: list[str]
        datasets: list[Dataset]

    totalCustomer: int
    sexData: Data
    maritalStatusData: Data
    incomeData: Data
    settlementData: Data
    occupationData: Data
    ageData: Data


@app.get("/api/v1/dashboard", response_model=DashboardGetResponse)
async def dashboard():
    Data = DashboardGetResponse.Data
    Dataset = DashboardGetResponse.Data.Dataset

    cur = con.cursor()

    total_customer: int = cur.execute("SELECT COUNT (*) FROM customers").fetchone()[0]

    males_count: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE sex = 0"
    ).fetchone()[0]
    females_count = total_customer - males_count
    gender_data = Data(
        labels=["Male", "Female"],
        datasets=[Dataset(label="Sexes", data=[males_count, females_count])],
    )

    singles_count: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE marital_status = 0"
    ).fetchone()[0]
    non_singles_count = total_customer - singles_count
    marital_status_data = Data(
        labels=["Single", "Non-single"],
        datasets=[
            Dataset(label="Marital status", data=[singles_count, non_singles_count])
        ],
    )

    incomes: list[float] = [x[0] for x in cur.execute("SELECT income FROM customers")]
    income_bins, income_edges = np.histogram(incomes, bins=5)
    income_labels = []
    for i in range(1, len(income_edges)):
        low: float = income_edges[i - 1].tolist()
        high: float = income_edges[i].tolist()
        label = f"{int(low/1000)}k-{int(high/1000)}k"
        income_labels.append(label)
    income_data = Data(
        labels=income_labels,
        datasets=[Dataset(label="Income", data=income_bins.tolist())],  # type: ignore
    )

    small_city_counts: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE settlement_size = 0"
    ).fetchone()[0]
    mid_sized_city_counts: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE settlement_size = 1"
    ).fetchone()[0]
    big_city_counts = total_customer - (small_city_counts + mid_sized_city_counts)
    settlement_data = Data(
        labels=["Small city", "Mid-sized city", "Big city"],
        datasets=[
            Dataset(
                label="Settlement size",
                data=[small_city_counts, mid_sized_city_counts, big_city_counts],
            )
        ],
    )

    unemployed_count: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE occupation = 0"
    ).fetchone()[0]
    skilled_employee_count: int = cur.execute(
        "SELECT COUNT (*) FROM customers WHERE occupation = 1"
    ).fetchone()[0]
    highly_qualified_employee = total_customer - (
        unemployed_count + skilled_employee_count
    )
    occupation_data = Data(
        labels=["Unemployed", "Skilled employee", "Highly qualified employee"],
        datasets=[
            Dataset(
                label="Settlement size",
                data=[
                    unemployed_count,
                    skilled_employee_count,
                    highly_qualified_employee,
                ],
            )
        ],
    )

    ages: list[int] = [x[0] for x in cur.execute("SELECT age FROM customers")]
    age_bins, age_edges = np.histogram(ages, bins=5)
    age_labels = []
    for i in range(1, len(age_bins)):
        low: float = age_edges[i - 1].tolist()
        high: float = age_edges[i].tolist()
        label = f"{low}-{high}"
        age_labels.append(label)
    age_data = Data(
        labels=age_labels,
        datasets=[Dataset(label="Age", data=age_bins.tolist())],  # type: ignore
    )

    return DashboardGetResponse(
        ageData=age_data,
        sexData=gender_data,
        incomeData=income_data,
        maritalStatusData=marital_status_data,
        occupationData=occupation_data,
        settlementData=settlement_data,
        totalCustomer=total_customer,
    )


class DetailsPostResponse(BaseModel):
    class Data(BaseModel):
        class Dataset(BaseModel):
            label: str
            data: list[float] | list[tuple[float, float]]

        labels: list[str]
        datasets: list[Dataset]

    data: Data
    dataAttribute: str


@app.get("/api/v1/details/age", response_model=DetailsPostResponse)
async def details_age():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []
    data = []
    for row in cur.execute(
        "SELECT cluster, MIN(age), MAX(age) FROM customers GROUP BY cluster"
    ):
        cluster, min_age, max_age = row
        labels.append(f"Cluster {cluster}")
        data.append((min_age, max_age))

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Age",
                    data=data,
                )
            ],
        ),
        dataAttribute="age",
    )


@app.get("/api/v1/details/sex", response_model=DetailsPostResponse)
async def details_sex():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []
    males_data = []
    females_data = []
    for row in cur.execute(
        "SELECT cluster, COUNT(CASE WHEN sex = 0 THEN 1 END), COUNT(CASE WHEN sex = 1 THEN 1 END) FROM customers GROUP BY cluster"
    ):
        cluster, males_count, females_count = row
        labels.append(f"Cluster {cluster}")
        males_data.append(males_count)
        females_data.append(females_count)

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Male",
                    data=males_data,
                ),
                Dataset(
                    label="Female",
                    data=females_data,
                ),
            ],
        ),
        dataAttribute="sex",
    )


@app.get("/api/v1/details/income", response_model=DetailsPostResponse)
async def details_income():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []
    data = []
    for row in cur.execute(
        "SELECT cluster, MIN(income), MAX(income) FROM customers GROUP BY cluster"
    ):
        cluster, min_income, max_income = row
        labels.append(f"Cluster {cluster}")
        data.append((min_income, max_income))

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Income",
                    data=data,
                ),
            ],
        ),
        dataAttribute="income",
    )


@app.get("/api/v1/details/education", response_model=DetailsPostResponse)
async def details_education():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []

    other_data = []
    high_school_data = []
    university_data = []
    graduate_school_data = []

    for row in cur.execute(
        "SELECT cluster, COUNT(CASE WHEN education = 0 THEN 1 END), COUNT(CASE WHEN education = 1 THEN 1 END), COUNT(CASE WHEN education = 2 THEN 1 END), COUNT(CASE WHEN education = 3 THEN 1 END) FROM customers GROUP BY cluster"
    ):
        (
            cluster,
            other_count,
            high_school_count,
            university_count,
            graduate_school_count,
        ) = row

        labels.append(f"Cluster {cluster}")

        other_data.append(other_count)
        high_school_data.append(high_school_count)
        university_data.append(university_count)
        graduate_school_data.append(graduate_school_count)

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Other",
                    data=other_data,
                ),
                Dataset(
                    label="High school",
                    data=high_school_data,
                ),
                Dataset(
                    label="University",
                    data=university_data,
                ),
                Dataset(
                    label="Graduate school",
                    data=graduate_school_data,
                ),
            ],
        ),
        dataAttribute="education",
    )


@app.get("/api/v1/details/marital-status", response_model=DetailsPostResponse)
async def details_marital_status():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []
    single_data = []
    non_single_data = []
    for row in cur.execute(
        "SELECT cluster, COUNT(CASE WHEN marital_status = 0 THEN 1 END), COUNT(CASE WHEN marital_status = 1 THEN 1 END) FROM customers GROUP BY cluster"
    ):
        cluster, singles_count, non_singles_count = row
        labels.append(f"Cluster {cluster}")
        single_data.append(singles_count)
        non_single_data.append(non_singles_count)

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Single",
                    data=single_data,
                ),
                Dataset(
                    label="Non single",
                    data=non_single_data,
                ),
            ],
        ),
        dataAttribute="marital-status",
    )


@app.get("/api/v1/details/occupation", response_model=DetailsPostResponse)
async def details_occupation():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []

    unemployed_data = []
    skilled_employee_data = []
    highly_qualified_employee_data = []

    for row in cur.execute(
        "SELECT cluster, COUNT(CASE WHEN occupation = 0 THEN 1 END), COUNT(CASE WHEN occupation = 1 THEN 1 END), COUNT(CASE WHEN occupation = 2 THEN 1 END) FROM customers GROUP BY cluster"
    ):
        (
            cluster,
            unemployed_count,
            skilled_employees_count,
            highly_qualified_employees_count,
        ) = row

        labels.append(f"Cluster {cluster}")

        unemployed_data.append(unemployed_count)
        skilled_employee_data.append(skilled_employees_count)
        highly_qualified_employee_data.append(highly_qualified_employees_count)

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Unemployed",
                    data=unemployed_data,
                ),
                Dataset(
                    label="Skilled employee",
                    data=skilled_employee_data,
                ),
                Dataset(
                    label="Highly qualified employee",
                    data=highly_qualified_employee_data,
                ),
            ],
        ),
        dataAttribute="occupation",
    )


@app.get("/api/v1/details/settlement-size", response_model=DetailsPostResponse)
async def details_settlement_size():
    Data = DetailsPostResponse.Data
    Dataset = DetailsPostResponse.Data.Dataset

    cur = con.cursor()

    labels = []

    small_city_data = []
    mid_sized_city_data = []
    big_city_data = []

    for row in cur.execute(
        "SELECT cluster, COUNT(CASE WHEN settlement_size = 0 THEN 1 END), COUNT(CASE WHEN settlement_size = 1 THEN 1 END), COUNT(CASE WHEN settlement_size = 2 THEN 1 END) FROM customers GROUP BY cluster"
    ):
        cluster, small_city_count, mid_sized_city_count, big_city_count = row

        labels.append(f"Cluster {cluster}")

        small_city_data.append(small_city_count)
        mid_sized_city_data.append(mid_sized_city_count)
        big_city_data.append(big_city_count)

    return DetailsPostResponse(
        data=Data(
            labels=sorted(labels),
            datasets=[
                Dataset(
                    label="Small city",
                    data=small_city_data,
                ),
                Dataset(
                    label="Mid-sized city",
                    data=mid_sized_city_data,
                ),
                Dataset(
                    label="Big city",
                    data=big_city_data,
                ),
            ],
        ),
        dataAttribute="settlement-size",
    )


class AnalyticsGetResponse(BaseModel):
    class Dataset(BaseModel):
        class Datum(BaseModel):
            x: float
            y: float

        label: str
        data: list[Datum]

    datasets: list[Dataset]


@app.get("/api/v1/analytics", response_model=AnalyticsGetResponse)
async def analytics():

    Dataset = AnalyticsGetResponse.Dataset
    Datum = AnalyticsGetResponse.Dataset.Datum
    cur = con.cursor()
    clusters: dict[int, list[tuple[float, float]]] = {}

    for row in cur.execute("SELECT cluster, x, y FROM customers_decomposed"):
        cluster, x, y = row
        try:
            clusters[cluster].append((x, y))
        except KeyError:
            clusters[cluster] = []

    return AnalyticsGetResponse(
        datasets=sorted(
            [
                Dataset(
                    label=f"Cluster {cluster}", data=[Datum(x=x, y=y) for x, y in data]
                )
                for cluster, data in clusters.items()
            ],
            key=lambda x: x.label,
        )
    )

class CustomerGetResponse(BaseModel):
    rowid: int
    sex: str
    marital_status: str
    age: int
    education: str
    income: str
    occupation: str
    settlement_size: str


@app.get("/api/v1/customers", response_model=list[CustomerGetResponse])
async def get_customers(limit: int = 5, offset: int = 0, filterid: str | None = None):
    cur = con.cursor()
    mapper = {
        "sex": {0: "Male", 1: "Female"},
        "marital_status": {0: "Single", 1: "Non-single"},
        "education": {0:"Other", 1:"High school", 2:"University", 3:"Graduate school" },
        "occupation": {0: "Unemployed", 1:"Skilled employee", 2:"Highly qualified employee"},
        "settlement_size": {0:"Small city", 1:"Mid-sized city", 2:"Big city" }
    }
    results = []
    if filterid is None:
        rows = cur.execute(
                "SELECT rowid, sex, marital_status, age, education, income, occupation, settlement_size FROM customers LIMIT (?) OFFSET (?)",
                (limit, offset)
            )
    else:
        rows = cur.execute(
            "SELECT rowid, sex, marital_status, age, education, income, occupation, settlement_size FROM customers WHERE rowid IN (?) LIMIT (?) OFFSET (?)",
            (filterid,limit, offset)
        )

    for (
        rowid,
        sex,
        marital_status,
        age,
        education,
        income,
        occupation,
        settlement_size,
    ) in cur.execute(
        "SELECT rowid, sex, marital_status, age, education, income, occupation, settlement_size FROM customers LIMIT (?) OFFSET (?)",
        (limit, offset)
    ):
        customer = CustomerGetResponse(
            rowid=rowid, sex=mapper["sex"][sex], marital_status=mapper["marital_status"][marital_status],
            age=age, education=mapper["education"][education], income=f"{int(income/1000)}k", occupation=mapper["occupation"][occupation],
            settlement_size=mapper["settlement_size"][settlement_size]
        )
        results.append(customer)

    return results


class CustomerPostPayload(BaseModel):
    sex: Literal["Male", "Female"]
    marital_status: Literal["Single", "Non-single"]
    age: int
    education: Literal["Other", "High school", "University", "Graduate school"]
    income: float
    occupation: Literal["Unemployed", "Skilled employee", "Highly qualified employee"]
    settlement_size: Literal["Small city", "Big city", "Mid-sized city"]


@app.post("/api/v1/customers")
async def add_customer(payload: CustomerPostPayload):
    row = [
        {"Male": 0, "Female": 1}[payload.sex],
        {"Single": 0, "Non-single": 1}[payload.marital_status],
        payload.age,
        {"Other": 0, "High school": 1, "University": 2, "Graduate school": 3}[
            payload.education
        ],
        payload.income,
        {"Unemployed": 0, "Skilled employee": 1, "Highly qualified employee": 2}[
            payload.occupation
        ],
        {
            "Small city": 0,
            "Mid-sized city": 1,
            "Big city": 2,
        }[payload.settlement_size],
    ]
    columns = [
        "sex",
        "marital_status",
        "age",
        "education" "income",
        "occupation",
        "settlement_size",
    ]
    df = pd.DataFrame(data=np.array(row), columns=np.array(columns))

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

    pca: PCA = joblib.load("assets/pca.joblib")
    decomposed_ndarray = pca.fit_transform(transformed_df)
    decomposed_df = pd.DataFrame(data=decomposed_ndarray, columns=np.array(["x", "y"]))

    df["cluster"] = y_pred
    transformed_df["cluster"] = y_pred
    decomposed_df["cluster"] = y_pred

    df.to_sql(name="customers", con=con)
    decomposed_df.to_sql(name="customers_decomposed", con=con)
    transformed_df.to_sql(name="customers_transformed", con=con)


@app.put("/api/v1/clusters")
async def refresh_clusters():
    cur = con.cursor()

    df = pd.read_sql(
        "SELECT sex, marital_status, age, education, income, occupation, settlement_size",
        con=con,
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

    scalers: dict[Literal["age", "income"], StandardScaler] = joblib.load(
        "assets/scalers.joblib"
    )
    encoders: dict[
        Literal["education", "marital_status", "occupation", "settlement_size", "sex"],
        OneHotEncoder,
    ] = joblib.load("assets/encoders.joblib")

    transformed_df, _, _ = transform_df(df.copy(), scalers, encoders)

    clusterer: KMeans = joblib.load("assets/kmeans.joblib")
    y_pred = clusterer.fit_predict(transformed_df)

    pca: PCA = joblib.load("assets/pca.joblib")
    decomposed_ndarray = pca.fit_transform(transformed_df)
    decomposed_df = pd.DataFrame(data=decomposed_ndarray, columns=np.array(["x", "y"]))

    df["cluster"] = y_pred
    transformed_df["cluster"] = y_pred
    decomposed_df["cluster"] = y_pred

    cur.execute("DROP TABLE IF EXISTS customers")
    cur.execute("DROP TABLE IF EXISTS customers_transformed")
    cur.execute("DROP TABLE IF EXISTS customers_decomposed")

    df.to_sql(name="customers", con=con)
    decomposed_df.to_sql(name="customers_decomposed", con=con)
    transformed_df.to_sql(name="customers_transformed", con=con)
