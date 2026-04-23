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
    "ml_ranking_dag",
    default_args=default_args,
    description="A DAG for ML ranking - ranks mutual fund schemes by performance",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the ranking task
def ranking_task():
    """
    This function:
    1. Reads the feature-engineered data
    2. Calculates performance scores for each scheme
    3. Ranks schemes (1st best, 2nd, 3rd, etc)
    4. Saves ranking results
    """
    import sys
    import pandas as pd
    from pathlib import Path
    
    # Add src to path so we can import our modules
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        # Import ranking module
        from machine_learning.ranking import rank_funds
        
        # Input file path (output from feature_engineering_dag)
        input_file = Path('/opt/airflow/data') / 'nav_with_features.csv'
        
        # Read input data
        df_features = pd.read_csv(input_file)
        
        # Output file path (where we save ranking results)
        output_file = Path('/opt/airflow/data') / 'schemes_rankings.csv'
        
        # Run ranking - returns dataframe with ranks
        schemes_ranked = rank_funds(df_features)
        
        # Save ranking results to file
        schemes_ranked.to_csv(output_file, index=False)
        
        print(f"Ranking completed. Results saved to {output_file}")
        print(f"Ranked {len(schemes_ranked)} schemes by performance score")
        
    except Exception as e:
        print(f"Error occurred during ranking: {e}")

# Create task
ranking_task_op = PythonOperator(
    task_id='ranking_task',
    python_callable=ranking_task,
    dag=dag,
)
