import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- URLs DIRETAS (RAW) DO GITHUB ---
# Substitua pelas suas URLs se forem diferentes.
# Certifique-se de que o link começa com "raw.githubusercontent.com"
EXCEL_URL = "https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/DADOSZSD065.XLSX"
LOGO_URL = "https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/logo.png"


# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
# st.set_page_config(layout="wide") # Opcional: para usar a largura total da tela

try:
    st.image(LOGO_URL, width=200)
except Exception as e:
    st.error(f"Não foi possível carregar a logo. Verifique a LOGO_URL. Erro: {e}")

st.title("Dashboard Kit Faturamento")


# --- CARREGAMENTO DOS DADOS ---
# Função com cache para não baixar o arquivo a cada interação
@st.cache_data
def load_data(url):
    try:
        df = pd.read_excel(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha do GitHub: {e}")
        st.info("Verifique se a URL da planilha está correta e é um link 'raw'.")
        return None

# Carrega os dados e continua a execução
df = load_data(EXCEL_URL)

# --- EXECUÇÃO DO DASHBOARD ---
# O código abaixo só é executado se o dataframe for carregado com sucesso
if df is not None:
    # --- PROCESSAMENTO DOS DADOS ---
    df["Data do documento"] = pd.to_datetime(df["Data do documento"])
    df["Mês"] = df["Data do documento"].dt.to_period("M").astype(str)

    st.sidebar.header("Filtros")
    
    # --- FILTROS NA BARRA LATERAL (LÓGICA ALTERADA) ---
    divisoes = sorted(df["Divisão"].dropna().unique())
    meses = sorted(df["Mês"].dropna().unique())

    # Filtros iniciam em branco (sem default)
    divisoes_selecionadas = st.sidebar.multiselect("Filtrar por Divisão", divisoes)
    meses_selecionados = st.sidebar.multiselect("Filtrar por Mês", meses)

    # Inicia com o dataframe completo
    df_filtrado = df

    # Aplica o filtro de divisão apenas se alguma opção for selecionada
    if divisoes_selecionadas:
        df_filtrado = df_filtrado[df_filtrado["Divisão"].isin(divisoes_selecionadas)]

    # Aplica o filtro de mês apenas se alguma opção for selecionada
    if meses_selecionados:
        df_filtrado = df_filtrado[df_filtrado["Mês"].isin(meses_selecionados)]

    # --- KPIs (Indicadores Chave de Performance) ---
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Notas Fiscais", df_filtrado["Nº documento de Faturamento"].nunique())
    col2.metric("Contratos", df_filtrado["Contrato"].nunique())
    col3.metric("Clientes", df_filtrado["Cliente"].nunique())
    col4.metric("Obras", df_filtrado["Código da Obra"].nunique())
    st.markdown("---")

    # --- GRÁFICOS DE EVOLUÇÃO MENSAL ---
    # Agrupamento dos dados por mês para os gráficos
    agrupado = df_filtrado.groupby("Mês").agg({
        "Nº documento de Faturamento": pd.Series.nunique,
        "Contrato": pd.Series.nunique,
        "Cliente": pd.Series.nunique,
        "Código da Obra": pd.Series.nunique
    }).reset_index().rename(columns={
        "Nº documento de Faturamento": "Notas Fiscais",
        "Contrato": "Contratos",
        "Cliente": "Clientes",
        "Código da Obra": "Obras"
    })

    st.subheader("Evolução Mensal")

    # Loop para criar um gráfico de barras para cada indicador
    for coluna in ["Notas Fiscais", "Contratos", "Clientes", "Obras"]:
        fig = px.bar(agrupado, x="Mês", y=coluna, text_auto=True,
                     title=f"{coluna} por Mês", labels={"Mês": "Mês", coluna: f"Quantidade de {coluna}"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

else:
    # Mensagem exibida se o carregamento dos dados falhar
    st.info("Aguardando o carregamento da planilha do GitHub para exibir o relatório.")
