
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
from io import BytesIO

# Logo
st.image("https://raw.githubusercontent.com/rodneic/relatorio_faturamento/main/logo.png", width=300)

# Título
st.title("Dashboard Kit Faturamento")

# Leitura do Excel via requests (mais confiável para GitHub)
url_dados = "https://raw.githubusercontent.com/rodneic/relatorio_faturamento/main/DADOSZSD065.XLSX"
response = requests.get(url_dados)
df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

# Conversão da data e extração do mês
df['Data do documento'] = pd.to_datetime(df['Data do documento'])
df['Mês'] = df['Data do documento'].dt.to_period('M').astype(str)

# Filtros
divisoes = sorted(df['Divisão'].dropna().unique())
meses = sorted(df['Mês'].dropna().unique())

divisoes_selecionadas = st.sidebar.multiselect("Filtrar por Divisão", divisoes, default=divisoes)
meses_selecionados = st.sidebar.multiselect("Filtrar por Mês", meses, default=meses)

df_filtrado = df[(df['Divisão'].isin(divisoes_selecionadas)) & (df['Mês'].isin(meses_selecionados))]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Notas Fiscais", df_filtrado['Nº documento de Faturamento'].nunique())
col2.metric("Contratos", df_filtrado['Contrato'].nunique())
col3.metric("Clientes", df_filtrado['Cliente'].nunique())
col4.metric("Obras", df_filtrado['Código da Obra'].nunique())

# Agrupamento por mês
agrupado = df_filtrado.groupby('Mês').agg({
    'Nº documento de Faturamento': pd.Series.nunique,
    'Contrato': pd.Series.nunique,
    'Cliente': pd.Series.nunique,
    'Código da Obra': pd.Series.nunique
}).reset_index().rename(columns={
    'Nº documento de Faturamento': 'Notas Fiscais',
    'Contrato': 'Contratos',
    'Cliente': 'Clientes',
    'Código da Obra': 'Obras'
})

st.subheader("Evolução Mensal")

for coluna in ['Notas Fiscais', 'Contratos', 'Clientes', 'Obras']:
    fig = px.bar(agrupado, x='Mês', y=coluna, text=coluna,
                 title=f"{coluna} por Mês", labels={'Mês': 'Mês', coluna: coluna})
    st.plotly_chart(fig, use_container_width=True)
