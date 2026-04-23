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
    "ml_clustering_dag",
    default_args=default_args,
    description="A DAG for ML clustering - groups mutual fund schemes into clusters",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the clustering task
def clustering_task():
    """
    This function:
    1. Reads the feature-engineered data
    2. Applies clustering algorithm (groups schemes into clusters)
    3. Saves clustering results
    """
    import sys
    import pandas as pd
    from pathlib import Path
    
    # Add src to path so we can import our modules
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        # Import clustering module
        from machine_learning.clustering import cluster_funds
        
        # Input file path (output from feature_engineering_dag)
        input_file = Path('/opt/airflow/data') / 'nav_with_features.csv'
        
        # Read input data
        df_features = pd.read_csv(input_file)
        
        # Output file path (where we save clustering results)
        output_file = Path('/opt/airflow/data') / 'schemes_clusters.csv'
        
        # Run clustering - returns dataframe with cluster assignments
        schemes_with_clusters, summary = cluster_funds(df_features, n_clusters=4)
        
        # Save clustering results to file
        schemes_with_clusters.to_csv(output_file, index=False)
        
        print(f"Clustering completed. Results saved to {output_file}")
        print(f"Clustered {len(schemes_with_clusters)} schemes into 4 clusters")
        
    except Exception as e:
        print(f"Error occurred during clustering: {e}")

# Create task
clustering_task_op = PythonOperator(
    task_id='clustering_task',
    python_callable=clustering_task,
    dag=dag,
)
