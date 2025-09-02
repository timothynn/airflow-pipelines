# Airflow Pipelines — Tiny, Opinionated (and a bit nerdy)

This repo is a minimal-but-solid data engineering playground powered by Apache Airflow running on Docker. It ships with:

- Postgres for both the Airflow metadata DB and user data
- A custom Airflow image with your Python deps baked in
- A handful of beginner → intermediate DAGs that do real I/O

It’s designed to be boringly reproducible, easy to hack on, and hard to misconfigure.

## 🧱 Architecture (high level)

- Airflow (`LocalExecutor`) in one container
- Postgres 15 in another container
- Bind mounts for `dags/` and `data/` so you can iterate locally
- Custom image built from `Dockerfile` installing `requirements.txt`

Data paths inside Airflow:
- `/opt/airflow/dags` → `./dags`
- `/opt/airflow/data` → `./data`

## ⚙️ Prerequisites

- Docker and Docker Compose
- Open ports: 8080 (Airflow UI), 5432 (Postgres)

## 🚀 Quickstart

```bash
# 1) Build the custom Airflow image with baked deps
docker compose build airflow

# 2) Start everything
docker compose up -d

# 3) Airflow UI
open http://localhost:8080   # or just visit in your browser
# Username: airflow  Password: airflow

# 4) List DAGs
docker exec airflow-pipelines-airflow-1 airflow dags list

# 5) Trigger a DAG (example)
docker exec airflow-pipelines-airflow-1 \
  airflow dags trigger etl_csv_to_postgres
```

## 📦 What’s in here

- `docker-compose.yaml` — two services: `postgres` and `airflow`
- `Dockerfile` — extends `apache/airflow:2.10.0`, installs Python deps as `airflow` user
- `requirements.txt` — runtime deps for DAGs (no `apache-airflow` here; base image has it)
- `dags/` — your DAGs
- `data/` — input/output data
- `pgdata/` — Postgres persistent volume (on host)

## 🧪 Included DAGs

All DAGs use `start_date=2025-01-01` and `catchup=False` unless noted. Paths refer to container paths under `/opt/airflow`.

- `etl_csv_to_postgres` (`dags/etl_csv_to_postgres.py`)
  - Reads `/opt/airflow/data/sample.csv` and inserts into Postgres table `people`.
- `api_to_postgres` (`dags/api_to_postgres.py`)
  - Fetches users from `jsonplaceholder.typicode.com` and inserts into `users`.
- `csv_to_parquet` (`dags/csv_to_parquet.py`)
  - Converts `sample.csv` → `sample.parquet` using `pandas.to_parquet`.
- `api_posts_to_file` (`dags/api_posts_to_file.py`)
  - Saves API posts JSON to `/opt/airflow/data/posts.json`.
- `postgres_table_counts` (`dags/postgres_table_counts.py`)
  - Writes row counts for `people` and `users` into `table_counts`.
- `transform_people_to_postgres` (`dags/transform_people_to_postgres.py`)
  - Adds `age_group` column to `sample.csv` and loads to `people_summary`.
- `daily_api_healthcheck` (`dags/daily_api_healthcheck.py`)
  - `BashOperator` curl check; fails if HTTP status ≠ 200.

## 🧰 Common operations

- Logs for Airflow container
```bash
docker compose logs airflow -f | cat
```

- List DAG runs for a DAG
```bash
docker exec airflow-pipelines-airflow-1 \
  airflow dags list-runs -d etl_csv_to_postgres
```

- Task test (runs task in isolation, no scheduler)
```bash
docker exec airflow-pipelines-airflow-1 \
  airflow tasks test csv_to_parquet convert_csv_to_parquet 2025-01-01T00:00:00+00:00
```

- Postgres console (inside container)
```bash
docker exec -it airflow-pipelines-postgres-1 \
  psql -U tim -d airflow_demo
```

## 🔁 Reproducibility & dependencies

Runtime deps are baked into the image. Update them here:

```
requirements.txt
pandas
requests
psycopg2-binary
pyarrow
fastparquet
```

Then rebuild and restart:
```bash
docker compose build airflow && docker compose up -d
```

Note: do not add `apache-airflow` to `requirements.txt` — the base image already includes it.

## 🔐 Credentials & config

- Postgres: user `tim`, password `secret`, db `airflow_demo`
- Airflow UI: user `airflow`, password `airflow`
- SQL Alchemy URL is provided via env var in `docker-compose.yaml`

Change these in `docker-compose.yaml` if you’re not just tinkering.

## 🗃️ Persistence

- Postgres data volume: `./pgdata` → `/var/lib/postgresql/data`
- `dags/` and `data/` are bind-mounted for rapid iteration

If you want immutable artifacts, move outputs out of bind mounts or use a volume.

## 🧪 Gotchas & troubleshooting

- Permission denied writing to `/opt/airflow/data`?
  - Ensure host dir is writable by container (e.g., `chmod -R a+rwX ./data`).
- Parquet write errors from pandas?
  - Ensure `pyarrow` or `fastparquet` is installed (already in `requirements.txt`).
- API calls failing intermittently?
  - Add `timeout=` and `resp.raise_for_status()` (already done), or retries/backoff.
- Airflow CLI `logs` subcommand not found?
  - Recent CLI switched semantics; prefer web UI logs or use `tasks test`.

## 📝 Real-world hiccups (and fixes)

- Mixed YAML styles in `docker-compose.yaml` env: switched to mapping style `KEY: VALUE`.
- Missing Python deps in container: baked them into image via `Dockerfile` + `requirements.txt`.
- Airflow container stopping: restarted stack, checked `docker compose logs airflow` for import errors.
- Parquet writes failing: installed `pyarrow`/`fastparquet` and set permissions on `data/`.
- Host dir permissions: granted write to `./data` so Airflow user could create outputs.

## 🧩 Extending

- Drop new DAGs into `dags/` and Airflow will auto-discover.
- Add libs → put them in `requirements.txt`, rebuild the image.
- For more executors (Celery, Kubernetes), change `AIRFLOW__CORE__EXECUTOR` and compose topology.

## 🧪 Verifying the stack

- Sanity check a DAG end-to-end:
```bash
docker exec airflow-pipelines-airflow-1 \
  airflow tasks test api_posts_to_file fetch_posts 2025-01-01T00:00:00+00:00
```
- Validate data landed:
```bash
docker exec airflow-pipelines-postgres-1 \
  psql -U tim -d airflow_demo -c 'SELECT COUNT(*) FROM users;'
```

---

Like all good labs, this one is small, self-contained, and opinionated. Pull the levers, break things, and then make them boring again. Happy DAGging! 🚀 