from datetime import datetime, timedelta
from google.cloud import bigquery
import os

def e_dia_util(data, feriados):
    if data.weekday() < 5 and data not in feriados:
        return True, "Dia Útil"
    elif data in feriados:
        return False, feriados[data]
    else:
        return False, "Fim de Semana"

def andar_prox_dia_util(data_atual, dias_calculados, feriados, prazo_count, tipo_contagem):
    while True:
        dia_util, motivo = e_dia_util(data_atual, feriados)
        if not dia_util:
            dias_calculados.append({
                "data": data_atual.strftime("%Y-%m-%d"),
                "considerado": False,
                "motivo": motivo
            })
            data_atual += timedelta(days=1)
        else:
            if tipo_contagem == "disponibilizacao":
                dias_calculados.append({
                    "data": data_atual.strftime("%Y-%m-%d"),
                    "considerado": False,
                    "motivo": "Disponibilização"
                })
                data_atual += timedelta(days=1)
            elif tipo_contagem == "contagem":
                prazo_count += 1
                dias_calculados.append({
                    "data": data_atual.strftime("%Y-%m-%d"),
                    "considerado": True,
                    "motivo": f"Dia {prazo_count} do prazo"
                })
                data_atual += timedelta(days=1)
            elif tipo_contagem == "ultimo_dia":
                dias_calculados.append({
                    "data": data_atual.strftime("%Y-%m-%d"),
                    "considerado": True,
                    "motivo": f"Dia {prazo_count} do prazo - dia não útil"
                })
                data_atual += timedelta(days=1)
            break

    return data_atual, dias_calculados, prazo_count

def get_feriados_from_bigquery(city: str) -> dict:
    client = bigquery.Client()
    query = f"""
    SELECT
    DATE(TIMESTAMP_MICROS(CAST(date / 1000 AS INT64))) AS data_evento,
    description
    FROM
    `prazos-project.prazos_trusted.trusted_tj_api_data`
    WHERE
    city = '{city}'
    ORDER BY data_evento DESC;
    """
    
    query_job = client.query(query)
    results = query_job.result()

    feriados = {}
    for row in results:
        data_evento = row['data_evento']
        feriados[data_evento] = row['description']

    return feriados

def calculate_prazo(tipo_processo:str = "cpc", 
    ato_publicacao:str = "publicacao", 
    data_inicial:datetime = datetime.now(), 
    prazo:int=5, 
    cidade:str="MOGI DAS CRUZES") -> list:

    # APP AUX PARAMETERS
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/miguelrezende/Documents/prazos_project/keys/prazos-project-080f299b982e.json"
    client = bigquery.Client()

    feriados = get_feriados_from_bigquery(city = cidade)
    data_atual = data_inicial
    dias_calculados = []
    prazo_count = 0

    # DIA DO ATO
    if ato_publicacao == "ato":
        dias_calculados.append({
            "data": data_atual.strftime("%Y-%m-%d"),
            "considerado": False,
            "motivo": "Dia do Ato"
        })
        data_atual += timedelta(days=1)
    # DIA DA PUBLICACAO DISPONIBILIZACAO 
    else:
        dias_calculados.append({
            "data": data_atual.strftime("%Y-%m-%d"),
            "considerado": False,
            "motivo": "Dia da Publicação"
        })
        data_atual += timedelta(days=1)
        data_atual, dias_calculados, prazo_count = andar_prox_dia_util(data_atual, dias_calculados, feriados, prazo_count, tipo_contagem="disponibilizacao")

    # ANDAR TODOS OS DIAS 
    while prazo_count < prazo:
        if tipo_processo == "cpc":
            data_atual, dias_calculados, prazo_count = andar_prox_dia_util(data_atual, dias_calculados, feriados, prazo_count, tipo_contagem="contagem")
        elif tipo_processo == "cpp":
            prazo_count += 1
            dias_calculados.append({
                "data": data_atual.strftime("%Y-%m-%d"),
                "considerado": True,
                "motivo": f"Dia {prazo_count} do prazo"
            })
            data_atual += timedelta(days=1)

    # AJUSTE ÚLTIMO DIA 
    if tipo_processo == "cpc":
        dias_calculados[-1]['motivo'] = dias_calculados[-1]['motivo'] + ' - último dia'
    elif tipo_processo == "cpp":
        dia_util, motivo = e_dia_util(data_atual, feriados)
        if dia_util:
            dias_calculados[-1]['motivo'] = dias_calculados[-1]['motivo'] + ' - último dia'
        else:
            dias_calculados[-1]['motivo'] = dias_calculados[-1]['motivo'] + ' - dia não útil'
            data_atual, dias_calculados, prazo_count = andar_prox_dia_util(data_atual, dias_calculados, feriados, prazo_count, tipo_contagem="ultimo_dia")
            dias_calculados[-1]['motivo'] = f'Dia {prazo_count} do prazo - último dia'

    return dias_calculados

# Exemplo de uso
calc = calculate_prazo(tipo_processo="cpp", 
    ato_publicacao="publicacao",
    data_inicial=datetime(2024, 8, 27).date(),
    prazo=5,
    cidade="MOGI DAS CRUZES")