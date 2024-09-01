import streamlit as st
import datetime
import sys
from datetime import datetime as dt
import pandas as pd

# Adiciona o diretório pai ao path para acessar o script de cálculo de prazos
sys.path.append('..')
from python_scripts.constants.api_constants import *
from python_scripts.calculate_deadlines import calculate_prazo

# Título principal
st.title("Calculadora de Prazos Processuais")

# Descrição inicial
st.markdown("""
Esta aplicação calcula prazos processuais com base no tipo de processo, ato, data inicial, cidade e quantidade de dias.
""")

# Layout de duas colunas para entradas do usuário
col1, col2 = st.columns(2)

with col1:
    tipo_processo = st.radio(
        'Tipo de Processo:',
        ("Código de Processo Civil", "Código de Processo Penal")
    )

    juntada_publicacao = st.radio(
        'Tipo de Ato:',
        ("Ato/Juntada", "Publicação")
    )

with col2:
    data_inicial = st.date_input(
        f"Data do(a) {juntada_publicacao}:", 
        dt.now().date(), 
        format="DD/MM/YYYY"
    )

    cidade = st.selectbox(
        "Comarca/Cidade do Processo:",
        city_list,
    )

    prazo = st.number_input("Prazo (dias):", min_value=1, value=5)

# Converter os inputs para o formato necessário para a função de cálculo
tipo_processo_mapping = {
    "Código de Processo Civil": "cpc",
    "Código de Processo Penal": "cpp"
}
ato_publicacao_mapping = {
    "Ato/Juntada": "ato",
    "Publicação": "publicacao"
}

tipo_processo = tipo_processo_mapping[tipo_processo]
ato_publicacao = ato_publicacao_mapping[juntada_publicacao]

# Adicionar um espaço antes do botão
st.markdown("---")



# Botão para calcular o prazo
if st.button("Calcular Prazo"):
    dias_calculados = calculate_prazo(
        tipo_processo=tipo_processo,
        ato_publicacao=ato_publicacao,
        data_inicial=data_inicial,
        prazo=prazo,
        cidade=cidade
    )

    # Transformar os resultados em um DataFrame para exibição
    df = pd.DataFrame(dias_calculados)
    df = df.drop("considerado", axis=1)

    # Renomear colunas para exibição mais clara
    df.columns = ["Data", "Motivo"]

    # Exibir a tabela com estilos
    st.markdown("### Resultado do Cálculo de Prazos")
    st.dataframe(df,hide_index=True)

    st.success("Cálculo de prazos concluído com sucesso!")

# Adicionar um rodapé
st.markdown("---")
st.markdown("© 2024 Calculadora de Prazos Processuais. Todos os direitos reservados.")