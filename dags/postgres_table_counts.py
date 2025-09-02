from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2


def record_counts():
    conn = psycopg2.connect(
        dbname="airflow_demo",
        user="tim",
        password="secret",
        host="postgres",
        port="5432",
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS table_counts (
            measured_at TIMESTAMP NOT NULL,
            table_name TEXT NOT NULL,
            row_count BIGINT NOT NULL
        );
    """)

    tables = ["people", "users"]
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO table_counts (measured_at, table_name, row_count) VALUES (NOW(), %s, %s);",
            (table, count),
        )

    conn.commit()
    cur.close()
    conn.close()


with DAG(
    dag_id="postgres_table_counts",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    PythonOperator(
        task_id="record_table_counts",
        python_callable=record_counts,
    ) 