import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests # NOVO: Para fazer chamadas à API

# --- URLs E CONSTANTES DO GITHUB ---
EXCEL_URL = "https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/DADOSZSD065.XLSX"
LOGO_URL = "https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/logo.png"

# NOVO: Informações do repositório para a API
OWNER = "rodneirac"
REPO = "BI_Faturamento"
FILE_PATH = "DADOSZSD065.XLSX"


# --- FUNÇÕES AUXILIARES ---

# NOVO: Função para buscar a data de última atualização do arquivo no GitHub
@st.cache_data(ttl=3600) # Cache de 1 hora
def get_last_update_date(owner, repo, path):
    """Busca a data do último commit de um arquivo específico via API do GitHub."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&page=1&per_page=1"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        commit_data = response.json()
        if commit_data:
            # Extrai a data e converte para o fuso horário local e formato brasileiro
            date_str = commit_data[0]['commit']['committer']['date']
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.astimezone().strftime('%d/%m/%Y às %H:%M')
        return "Não foi possível obter a data."
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API do GitHub: {e}")
        return "Erro de conexão ao verificar a data."

@st.cache_data
def load_data(url):
    """Carrega os dados da planilha a partir de uma URL."""
    try:
        df = pd.read_excel(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha do GitHub: {e}")
        return None

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
try:
    st.image(LOGO_URL, width=200)
except Exception:
    st.error("Não foi possível carregar a logo. Verifique a LOGO_URL.")

st.title("Dashboard Kit Faturamento")

# NOVO: Busca e exibe a data de atualização
last_update = get_last_update_date(OWNER, REPO, FILE_PATH)
st.caption(f"Dados atualizados em: **{last_update}**")


# --- CARREGAMENTO PRINCIPAL E EXECUÇÃO DO DASHBOARD ---
df = load_data(EXCEL_URL)

if df is not None:
    # --- PROCESSAMENTO DOS DADOS ---
    df["Data do documento"] = pd.to_datetime(df["Data do documento"])
    df["Mês"] = df["Data do documento"].dt.to_period("M").astype(str)

    st.sidebar.header("Filtros")
    
    # --- FILTROS NA BARRA LATERAL ---
    divisoes = sorted(df["Divisão"].dropna().unique())
    meses = sorted(df["Mês"].dropna().unique())

    divisoes_selecionadas = st.sidebar.multiselect("Filtrar por Divisão", divisoes)
    meses_selecionados = st.sidebar.multiselect("Filtrar por Mês", meses)

    df_filtrado = df
    if divisoes_selecionadas:
        df_filtrado = df_filtrado[df_filtrado["Divisão"].isin(divisoes_selecionadas)]
    if meses_selecionados:
        df_filtrado = df_filtrado[df_filtrado["Mês"].isin(meses_selecionados)]

    # --- KPIs ---
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Notas Fiscais", df_filtrado["Nº documento de Faturamento"].nunique())
    col2.metric("Contratos", df_filtrado["Contrato"].nunique())
    col3.metric("Clientes", df_filtrado["Cliente"].nunique())
    col4.metric("Obras", df_filtrado["Código da Obra"].nunique())
    st.markdown("---")

    # --- GRÁFICOS ---
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

    for coluna in ["Notas Fiscais", "Contratos", "Clientes", "Obras"]:
        fig = px.bar(agrupado, x="Mês", y=coluna, text_auto=True,
                     title=f"{coluna} por Mês", labels={"Mês": "Mês", coluna: f"Quantidade de {coluna}"})
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Aguardando o carregamento da planilha do GitHub para exibir o relatório.")
