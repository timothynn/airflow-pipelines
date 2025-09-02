import requests
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def fetch_and_load():
    resp = requests.get("https://jsonplaceholder.typicode.com/users")
    data = resp.json()

    conn = psycopg2.connect(
        dbname="airflow_demo",
        user="tim",
        password="secret",
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INT, name TEXT, email TEXT);")

    for user in data:
        cur.execute("INSERT INTO users (id, name, email) VALUES (%s, %s, %s);",
                    (user["id"], user["name"], user["email"]))
    
    conn.commit()
    cur.close()
    conn.close()

with DAG(
    "api_to_postgres",
    start_date=datetime(2025,1,1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    PythonOperator(
        task_id="fetch_load_api",
        python_callable=fetch_and_load
    )

