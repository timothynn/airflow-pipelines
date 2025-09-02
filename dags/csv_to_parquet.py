from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd


def csv_to_parquet():
    src_path = "/opt/airflow/data/sample.csv"
    dst_path = "/opt/airflow/data/sample.parquet"
    df = pd.read_csv(src_path)
    df.to_parquet(dst_path, index=False)


with DAG(
    dag_id="csv_to_parquet",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    PythonOperator(
        task_id="convert_csv_to_parquet",
        python_callable=csv_to_parquet,
    ) 