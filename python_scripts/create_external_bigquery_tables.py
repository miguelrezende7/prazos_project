import os
from datetime import datetime
from google.cloud import bigquery

# Configurações
project_id = "prazos-project"
dataset_id = "prazos_raw"

tables_data = [
    {
        'table_id' : 'tj_api_data',
        'bucket_uris' : ["gs://prazos_bucket/*"]
    }
]

# Caminho para o arquivo de credenciais
# credentials_path = '/Users/miguelrezende/Documents/prazos_project/keys/prazos-project-080f299b982e.json'
credentials_path = '/opt/keys/prazos-project-080f299b982e.json'

# Configurar a variável de ambiente para as credenciais
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

def check_table_exists(dataset_id, table_id):
    print(f"Checking table existence - table: {table_id}")
    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)
    try:
        client.get_table(table_ref)
        print(f"Table already exists")
        return True
    except Exception as e:
        print(f"Table does not exist")
        return False

def create_external_table(project_id, dataset_id, table_id, uris):
    print("creating table")
    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset_id).table(table_id)
    
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = uris
    
    table = bigquery.Table(table_ref)
    table.external_data_configuration = external_config
    
    client.create_table(table)
    print(f"Created external table {table_id}")

# Função para verificar e criar tabela
def verify_and_create_table():
    
    for table_data in tables_data:
        if not check_table_exists(dataset_id, table_data['table_id']):
            create_external_table(project_id, dataset_id, table_data['table_id'], table_data['bucket_uris'])

def main():
    
    verify_and_create_table()

if __name__ == "__main__":
    main()