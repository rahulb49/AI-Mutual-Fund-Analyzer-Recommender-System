from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Default arguments for all tasks
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    "feature_engineering_dag",
    default_args=default_args,
    description="A DAG for feature engineering - transforms raw NAV data into features",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the feature engineering task
def feature_engineering_task():
    """
    This function:
    1. Reads the NAV data file from /opt/airflow/data
    2. Creates new features (columns) from raw data
    3. Saves the processed data to output file
    """
    import sys
    from pathlib import Path
    
    # Add src to path so we can import our modules
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        # Import feature engineering module
        from processing.feature_engineering import prepare_features
        
        # Input file path (output from data_ingestion_dag)
        input_file = Path('/opt/airflow/data') / 'NAVAll.txt'
        
        # Output file path (where we save processed features)
        output_file = Path('/opt/airflow/data') / 'nav_with_features.csv'
        
        # Run feature engineering
        prepare_features(input_file, output_file)
        
        print(f"Feature engineering completed. Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error occurred during feature engineering: {e}")

# Create task
feature_task = PythonOperator(
    task_id='feature_engineering_task',
    python_callable=feature_engineering_task,
    dag=dag,
)
