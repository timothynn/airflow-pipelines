from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2


def transform_and_load():
    df = pd.read_csv("/opt/airflow/data/sample.csv")
    def age_group(age: int) -> str:
        if age < 18:
            return "minor"
        if age < 40:
            return "adult"
        return "senior"

    df["age_group"] = df["age"].apply(age_group)

    conn = psycopg2.connect(
        dbname="airflow_demo",
        user="tim",
        password="secret",
        host="postgres",
        port="5432",
    )
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS people_summary (name TEXT, age INT, age_group TEXT);"
    )

    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO people_summary (name, age, age_group) VALUES (%s, %s, %s);",
            (row["name"], int(row["age"]), row["age_group"]),
        )

    conn.commit()
    cur.close()
    conn.close()


with DAG(
    dag_id="transform_people_to_postgres",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    PythonOperator(
        task_id="transform_and_load_people",
        python_callable=transform_and_load,
    ) 