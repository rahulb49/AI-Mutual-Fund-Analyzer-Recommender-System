from airflow import DAG #is the main container for all workflow logic.
from airflow.operators.python import PythonOperator #allows you to execute Python functions as tasks in a DAG.
from datetime import datetime, timedelta #needed to set start dates and retry delays for the DAG.


# Default arguments
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    "data_ingestion_dag",
    default_args=default_args,
    description="A DAG for data ingestion",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)


# Task 1: Data ingestion task (placeholder)
def data_ingestion_task():
    import sys
    import pandas as pd
    from pathlib import Path

    # Add src to path
    sys.path.insert(0,'/opt/airflow/src')

    try:
        from ingestion.nav_ingestion import download_nav_data, AMFI_NAV_URL, Local_file_path
        file_path = Path(Local_file_path) / "NAVAll.txt"
        download_nav_data(AMFI_NAV_URL, file_path)
        print(f"Data ingested successfully and saved to {file_path}")
    except Exception as e:
        print(f"Error occurred while ingesting data: {e}")


task1 = PythonOperator(
    task_id='data_ingestion_task',
    python_callable=data_ingestion_task,
    dag=dag,
)
