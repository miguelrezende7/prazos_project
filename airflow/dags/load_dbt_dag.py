from airflow import DAG
from airflow_dbt.operators.dbt_operator import DbtRunOperator
from datetime import datetime

default_args = {
    'owner': 'miguel',
    'start_date': datetime(2023, 8, 1),
    'retries': 1
}

with DAG('load_parquet_to_bq_dag',
         default_args=default_args,
         schedule_interval=None) as dag:

    dbt_run = DbtRunOperator(
        task_id='dbt_run',
        dir='/opt/dbt_project',
        profiles_dir='/opt/dbt_project',
        models='load_parquet_to_test'
    )

    dbt_run