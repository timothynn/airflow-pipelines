from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2

def load_csv_to_postgres():
    conn = psycopg2.connect(
        dbname="airflow_demo",
        user="tim",
        password="secret",
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS people (id SERIAL PRIMARY KEY, name TEXT, age INT);")

    df = pd.read_csv("/opt/airflow/data/sample.csv")
    for _, row in df.iterrows():
        cur.execute("INSERT INTO people (name, age) VALUES (%s, %s);", (row['name'], row['age']))
    
    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id="etl_csv_to_postgres",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id="load_csv",
        python_callable=load_csv_to_postgres,
    )

