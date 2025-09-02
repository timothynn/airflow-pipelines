import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests


def fetch_posts_to_file():
    url = "https://jsonplaceholder.typicode.com/posts"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    posts = resp.json()
    out_path = "/opt/airflow/data/posts.json"
    with open(out_path, "w") as f:
        json.dump(posts, f, indent=2)


with DAG(
    dag_id="api_posts_to_file",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    PythonOperator(
        task_id="fetch_posts",
        python_callable=fetch_posts_to_file,
    ) 