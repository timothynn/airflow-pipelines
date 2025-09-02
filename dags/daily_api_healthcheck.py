from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Checks that the endpoint returns HTTP 200; fails otherwise
curl_cmd = (
    "status=$(curl -s -o /dev/null -w '%{http_code}' https://jsonplaceholder.typicode.com/users) && "
    "echo HTTP:$status && [ \"$status\" = \"200\" ]"
)

with DAG(
    dag_id="daily_api_healthcheck",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    BashOperator(
        task_id="api_healthcheck",
        bash_command=curl_cmd,
    ) 