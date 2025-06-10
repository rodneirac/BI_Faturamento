import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# --- URLs E CONSTANTES DO GITHUB ---

# -- ALTERADO/NOVO --: Nomes dos arquivos ajustados conforme solicitado.
ARQUIVO_DADOS_HISTORICO = "DADOSHISTO.XLSX"
ARQUIVO_DADOS_ATUAL = "DADOSATUAL.XLSX"

URL_DADOS_HISTORICO = f"https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/{ARQUIVO_DADOS_HISTORICO}"
URL_DADOS_ATUAL = f"https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/{ARQUIVO_DADOS_ATUAL}"

LOGO_URL = "https://raw.githubusercontent.com/rodneirac/BI_Faturamento/main/logo.png"

# Informações do repositório para a API
OWNER = "rodneirac"
REPO = "BI_Faturamento"


# --- FUNÇÕES AUXILIARES ---

@st.cache_data(ttl=3600)
def get_latest_update_info(owner, repo, file_paths):
    """Verifica a data do último commit para uma lista de arquivos e retorna a mais recente."""
    latest_date = None
    latest_file = None

    for path in file_paths:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}&page=1&per_page=1"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            commit_data = response.json()
            if commit_data:
                date_str = commit_data[0]['commit']['committer']['date']
                current_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
                    latest_file = path
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API do GitHub para o arquivo {path}: {e}")
            continue
            
    if latest_date:
        local_date_str = latest_date.astimezone().strftime('%d/%m/%Y às %H:%M')
        return f"**{local_date_str}** (arquivo: *{latest_file}*)"
    
    return "Não foi possível obter a data de atualização."


@st.cache_data
def load_data(url):
    """Carrega os dados da planilha a partir de uma URL, tratando erros."""
    try:
        df = pd.read_excel(url)
        return df
    except Exception as e:
        print(f"Aviso: Não foi possível carregar o arquivo da URL {url}. Erro: {e}")
        return None

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
try:
    st.image(LOGO_URL, width=200)
except Exception:
    st.error("Não foi possível carregar a logo. Verifique a LOGO_URL.")

st.title("Dashboard Kit Faturamento")

latest_update_info = get_latest_update_info(OWNER, REPO, [ARQUIVO_DADOS_HISTORICO, ARQUIVO_DADOS_ATUAL])
st.caption(f"Dados atualizados em: {latest_update_info}")


# --- CARREGAMENTO PRINCIPAL E EXECUÇÃO DO DASHBOARD ---
df_historico = load_data(URL_DADOS_HISTORICO)
df_atual = load_data(URL_DADOS_ATUAL)

dataframes_para_unir = []
if df_historico is not None:
    dataframes_para_unir.append(df_historico)
if df_atual is not None:
    dataframes_para_unir.append(df_atual)

if dataframes_para_unir:
    df = pd.concat(dataframes_para_unir, ignore_index=True)
    df.drop_duplicates(inplace=True)

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
    st.markdown("### Indicadores Gerais")
    
    # -- ALTERADO/NOVO --: Formatação dos KPIs com separador de milhar
    kpi_notas = df_filtrado["Nº documento de Faturamento"].nunique()
    kpi_contratos = df_filtrado["Contrato"].nunique()
    kpi_clientes = df_filtrado["Cliente"].nunique()
    kpi_obras = df_filtrado["Código da Obra"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Notas Fiscais", f"{kpi_notas:,}".replace(",", "."))
    col2.metric("Contratos", f"{kpi_contratos:,}".replace(",", "."))
    col3.metric("Clientes", f"{kpi_clientes:,}".replace(",", "."))
    col4.metric("Obras", f"{kpi_obras:,}".replace(",", "."))

    # -- ALTERADO/NOVO --: Novos KPIs de Média
    st.markdown("### Indicadores de Média")

    # Calcula as médias com segurança para evitar divisão por zero
    avg_nf_por_cliente = (kpi_notas / kpi_clientes) if kpi_clientes > 0 else 0
    avg_nf_por_contrato = (kpi_notas / kpi_contratos) if kpi_contratos > 0 else 0
    avg_clientes_por_obra = (kpi_clientes / kpi_obras) if kpi_obras > 0 else 0
    
    col5, col6, col7 = st.columns(3)
    col5.metric("NF por Cliente", f"{avg_nf_por_cliente:.2f}".replace(".", ","))
    col6.metric("NF por Contrato", f"{avg_nf_por_contrato:.2f}".replace(".", ","))
    col7.metric("Clientes por Obra", f"{avg_clientes_por_obra:.2f}".replace(".", ","))
    
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
    st.error("Não foi possível carregar nenhuma das planilhas de dados. Verifique os nomes e links no GitHub.")
