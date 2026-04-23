from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

# Default arguments for all tasks
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create Master DAG
dag = DAG(
    "master_orchestration_dag",
    default_args=default_args,
    description="Master DAG - orchestrates the entire pipeline: data_ingestion -> feature_engineering -> clustering -> ranking -> recommendations",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Task 1: Trigger data ingestion
trigger_data_ingestion = TriggerDagRunOperator(
    task_id='trigger_data_ingestion_task',
    trigger_dag_id='data_ingestion_dag',
    dag=dag,
)

# Task 2: Trigger feature engineering (after data ingestion completes)
trigger_feature_engineering = TriggerDagRunOperator(
    task_id='trigger_feature_engineering_task',
    trigger_dag_id='feature_engineering_dag',
    dag=dag,
)

# Task 3: Trigger clustering (after feature engineering completes)
trigger_clustering = TriggerDagRunOperator(
    task_id='trigger_clustering_task',
    trigger_dag_id='ml_clustering_dag',
    dag=dag,
)

# Task 4: Trigger ranking (after feature engineering completes)
trigger_ranking = TriggerDagRunOperator(
    task_id='trigger_ranking_task',
    trigger_dag_id='ml_ranking_dag',
    dag=dag,
)

# Task 5: Trigger recommendations (after clustering and ranking complete)
trigger_recommendations = TriggerDagRunOperator(
    task_id='trigger_recommendations_task',
    trigger_dag_id='ml_recommendation_dag',
    dag=dag,
)

# Define task dependencies (order of execution):
# 1. First run data ingestion
# 2. Then run feature engineering
# 3. Then run clustering AND ranking in parallel
# 4. Finally run recommendations

trigger_data_ingestion >> trigger_feature_engineering
trigger_feature_engineering >> [trigger_clustering, trigger_ranking]
[trigger_clustering, trigger_ranking] >> trigger_recommendations
