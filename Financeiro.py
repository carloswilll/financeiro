import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gerenciador Financeiro", layout="wide")
st.title("📊 Meu Painel Financeiro Pessoal")

# URL do arquivo CSV no GitHub (formato raw)
url = "https://raw.githubusercontent.com/carloswilll/financeiro/main/FINANCEIRO.CSV"

# Leitura e tratamento de dados
df = pd.read_csv(url, sep=";")
df['Valor'] = df['Valor'].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)

# Filtros
with st.sidebar:
    st.header("Filtros")
    data_inicio = st.date_input("Data inicial", df['Data'].min())
    data_fim = st.date_input("Data final", df['Data'].max())
    grupo = st.multiselect("Grupo", df['Grupo de Dias'].unique(), default=df['Grupo de Dias'].unique())

df_filtrado = df[
    (df['Data'] >= pd.to_datetime(data_inicio)) &
    (df['Data'] <= pd.to_datetime(data_fim)) &
    (df['Grupo de Dias'].isin(grupo))
]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Gasto", f"R$ {df_filtrado['Valor'].sum():,.2f}")
col2.metric("📅 Média por Dia", f"R$ {df_filtrado.groupby('Data')['Valor'].sum().mean():.2f}")
col3.metric("⚠️ Gastos Excessivos", df_filtrado[df_filtrado['Gasto Excessivo'] == "Acima da Média"].shape[0])

# Gráfico por tipo de despesa
st.subheader("📌 Gasto por Tipo de Despesa")
fig = px.bar(df_filtrado.groupby('Tipo de Despesa')['Valor'].sum().sort_values(), 
             orientation='h', title="Gasto por Tipo de Despesa", labels={'value': 'Total (R$)', 'Tipo de Despesa': 'Categoria'})
st.plotly_chart(fig, use_container_width=True)

# Tabela detalhada
st.subheader("📋 Tabela Detalhada")
st.dataframe(df_filtrado.sort_values("Data", ascending=False), use_container_width=True)
