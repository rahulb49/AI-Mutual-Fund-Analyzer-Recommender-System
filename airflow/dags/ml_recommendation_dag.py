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
    "ml_recommendation_dag",
    default_args=default_args,
    description="A DAG for ML recommendations - generates investment recommendations based on clustering and ranking",
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the recommendation task
def recommendation_task():
    """
    This function:
    1. Reads the feature-engineered data
    2. Calculates performance scores and cluster assignments
    3. Generates personalized recommendations
    4. Saves recommendations to file
    """
    import sys
    import pandas as pd
    from pathlib import Path
    
    # Add src to path so we can import our modules
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        # Import recommendation module
        from machine_learning.recommendation import recommend_funds
        
        # Input file path (output from feature_engineering_dag)
        input_file = Path('/opt/airflow/data') / 'nav_with_features.csv'
        
        # Read input data
        df_features = pd.read_csv(input_file)
        
        # Output file path (where we save recommendations)
        output_file = Path('/opt/airflow/data') / 'scheme_recommendations.csv'
        
        # Generate recommendations for moderate risk profile
        # You can change this to 'low' or 'high' for different risk profiles
        recommended_schemes = recommend_funds(
            df_features, 
            risk_profile='moderate', 
            top_n=10
        )
        
        # Save recommendations to file
        recommended_schemes.to_csv(output_file, index=False)
        
        print(f"Recommendations generated. Results saved to {output_file}")
        print(f"Generated recommendations for {len(recommended_schemes)} schemes")
        
    except Exception as e:
        print(f"Error occurred during recommendation generation: {e}")

# Create task
recommendation_task_op = PythonOperator(
    task_id='recommendation_task',
    python_callable=recommendation_task,
    dag=dag,
)
