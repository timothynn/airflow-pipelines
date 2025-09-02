FROM apache/airflow:2.10.0

# Install Python deps as the 'airflow' user (required by the base image)
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt 