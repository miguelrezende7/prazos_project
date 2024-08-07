import requests
import pandas as pd
import datetime

################################################################################
# AUX FUNCTIONS 
################################################################################


##### API FUNCTIONS #####

def get_ranged_data_list(ranged_data: dict) -> list :

    initial_date_timestamp = int(ranged_data['DataInicial'][6:19])
    lastdate_timestamp = int(ranged_data['DataFinal'][6:19])
    
    initial_datetime = datetime.datetime.fromtimestamp(initial_date_timestamp / 1000)
    lastdate_datetime = datetime.datetime.fromtimestamp(lastdate_timestamp / 1000)

    delta_days = (lastdate_datetime-initial_datetime).days
    
    date_list = []
    
    if delta_days == 0:
        date_list = [initial_datetime]
    else:
        for i in range(delta_days+1):
            current_date = initial_datetime + datetime.timedelta(days=i)
            date_list.append(current_date)

    return date_list

def get_ranged_dict_list(api_data: dict, city:str, year:str,date_list: list=[], endpoint:str = 'suspensoes') -> list:
        
    dict_list = []
        
    if endpoint == 'suspensoes':
        dje = api_data['DJE']
        for current_date in date_list:
            current_dict = {
                'city' : city,
                'year' : year,
                'date' : current_date,
                'description' : api_data['Descricao'],
                'dje' : dje,
                'type' : 'suspensao'
            }
            dict_list.append(current_dict)
        
    
    elif endpoint == 'feriados':    
        current_date_timestamp = int(api_data['DataFeriado'][6:19])
        current_date_datetime = datetime.datetime.fromtimestamp(current_date_timestamp / 1000)
        current_dict = {
            'city' : city,
            'year' : year,
            'date' : current_date_datetime,
            'description' : api_data['Descricao'],
            'dje' : '',
            'type' : 'feriado'
        }
        dict_list.append(current_dict)

    return dict_list
        
def get_data_from_api(city:str, year:str, endpoint:str ='feriados') -> dict:

    base_url_feriados = 'https://www.tjsp.jus.br/CanaisComunicacao/Feriados/PesquisarFeriados?'
    base_url_suspensoes = 'https://www.tjsp.jus.br/CanaisComunicacao/Feriados/PesquisarSuspensoes?'
   
    if endpoint == 'feriados':
        url = f'{base_url_feriados}nomeMunicipio={city}&ano={year}'
    elif endpoint == 'suspensoes':
        url = f'{base_url_suspensoes}nomeMunicipio={city}&ano={year}'

    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        
          
        return dados

    else:
        print(f"Erro ao buscar dados: {response.status_code}")
        return None

##### GOOGLE CLOUD FUNCTIONS #####

def save_parquet_to_gcs(df: pd.DataFrame):
    bucket_base_path = 'gs://prazos_bucket/'
    current_date = datetime.datetime.now()
    parquet_folder = current_date.strftime('%Y/%m/%d/')
    parquet_filename = current_date.strftime('%H%M%S') + '_file.parquet'
    parquet_path = bucket_base_path + parquet_folder + parquet_filename
    # credentials_path = '/Users/miguelrezende/Documents/prazos_project/keys/prazos-project-080f299b982e.json'
    credentials_path = '/opt/airflow/keys/prazos-project-080f299b982e.json'
    
    try:
        print(f'Saving file: {parquet_path} in Google Cloud Storage')
        df.to_parquet(parquet_path, index=False, storage_options={"token": credentials_path})
    except Exception as e:
       print(f'Error saving file: {parquet_path} in Google Cloud Storage\n{e}')


def main():

    city_list = ['Suzano','Mogi das Cruzes']
    year_list = ['2023','2024']
    endpoint_type_list = ['feriados', 'suspensoes']
    df = pd.DataFrame()
   
    print('Getting data from API')
    for endpoint in endpoint_type_list:
        print(f'\nEndpoint: {endpoint}')
        for city in city_list:
            for year in year_list:
                try:
                    print(f'{city} - {year}')
                    dados = get_data_from_api(endpoint=endpoint, city=city, year=year)
                    for valor in dados['data']:
                        if endpoint == 'suspensoes':
                            date_list = get_ranged_data_list(ranged_data=valor)
                        elif endpoint == 'feriados':
                            date_list = []
                        dict_list = get_ranged_dict_list(date_list=date_list, api_data=valor, city=city, year=year, endpoint=endpoint)
                        df_current = pd.DataFrame(dict_list)
                        df = pd.concat([df,df_current],axis=0)
                    
                except Exception as e:
                    print(f'Error getting data from API: \nEndpoint: {endpoint}\nCity: {city}\nYear: {year}\n')                  

    save_parquet_to_gcs(df)



if __name__ == "__main__":
    main()
                
           

                    


    

  