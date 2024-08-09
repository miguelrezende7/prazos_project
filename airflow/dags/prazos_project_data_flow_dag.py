from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow_dbt.operators.dbt_operator import DbtRunOperator

from datetime import datetime,timedelta
import sys
import os

default_args = {
    'owner': 'miguelrezende',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'execute_prazos_project_data_flow',
    default_args=default_args,
    description='Execute tasks for prazos project',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 7, 1),
    catchup=False,
)

# Python Script paths
script_path_get_api_data = "/opt/python_scripts/get_api_data_script.py"
script_path_create_external_bigquery_tables = "/opt/python_scripts/create_external_bigquery_tables.py"

# Criando uma tarefa para executar o script Python usando o BashOperator
get_api_data = BashOperator(
    task_id='get_api_data',
    bash_command=f'python3 {script_path_get_api_data} 2>&1',
    dag=dag,
)

create_external_bigquery_tables = BashOperator(
    task_id='create_external_bigquery_tables',
    bash_command=f'python3 {script_path_create_external_bigquery_tables} 2>&1',
    dag=dag,
)

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/dbt_project/ && dbt run --profile prazos_profile_airflow',
    dag=dag,
)


# Tasks Execution
create_external_bigquery_tables >> get_api_data >> dbt_run

