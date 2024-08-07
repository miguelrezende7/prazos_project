from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
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
    'execute_get_api_data_script',
    default_args=default_args,
    description='A simple DAG to execute a Python script',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 7, 1),
    catchup=False,
)

# Definindo o caminho completo para o script
script_path = "/opt/airflow/python_scripts/get_api_data_script.py"

# Criando uma tarefa para executar o script Python usando o BashOperator
run_python_script = BashOperator(
    task_id='run_python_script',
    bash_command=f'python3 {script_path} 2>&1',
    dag=dag,
)


# Definindo a ordem das tarefas
run_python_script








# SCRIPT_PATH = '/opt/airflow/dags/scripts/get_api_data_script.py'

# def execute_script():
#     # Adiciona o diretório do script ao path
#     script_dir = os.path.dirname(SCRIPT_PATH)
#     sys.path.append(script_dir)
    
#     # Importa e executa o script
#     script_name = os.path.basename(SCRIPT_PATH).replace('.py', '')
#     script_module = __import__(script_name)
#     script_module.main()

# dag = DAG(
#     'execute_python_script',
#     description='DAG to execute a Python script',
#     schedule_interval='@daily',
#     start_date=datetime(2024, 7, 1),
#     catchup=False
# )

# # Define o PythonOperator
# run_script_task = PythonOperator(
#     task_id='run_script',
#     python_callable=execute_script,
#     dag=dag
# )

# # Define a ordem das tarefas na DAG
# run_script_task