import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Meu Painel Financeiro Pessoal", layout="wide")

# 🎯 1. Cabeçalho
st.title("💰 Meu Painel Financeiro Pessoal")

# 📁 Upload seguro de arquivo
uploaded_file = st.file_uploader("📁 Faça upload do arquivo financeiro (.csv ou .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Tipo de arquivo não suportado. Por favor, envie um .csv ou .xlsx.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
else:
    st.warning("Por favor, carregue um arquivo para visualizar o dashboard.")
    st.stop()

# 🧼 Limpeza e preparação de dados
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['Data', 'Valor'])
df['Ano'] = df['Data'].dt.year
df['Mês'] = df['Data'].dt.month
df['Dia da Semana'] = df['Data'].dt.day_name()

# 🎛️ Filtros interativos
with st.sidebar:
    st.header("🎚️ Filtros")

    data_min, data_max = df['Data'].min(), df['Data'].max()
    data_range = st.date_input("📅 Intervalo de datas", [data_min, data_max])

    meses = st.multiselect("🗓️ Mês", sorted(df['Mês'].unique()), default=sorted(df['Mês'].unique()))
    anos = st.multiselect("📆 Ano", sorted(df['Ano'].unique()), default=sorted(df['Ano'].unique()))
    pessoas = st.multiselect("👤 Pessoa", sorted(df['Pessoa'].dropna().unique()), default=sorted(df['Pessoa'].dropna().unique()))
    tipos = st.multiselect("📂 Tipo de Despesa", sorted(df['Tipo'].dropna().unique()), default=sorted(df['Tipo'].dropna().unique()))
    bancos = st.multiselect("🏦 Banco", sorted(df['Banco'].dropna().unique()), default=sorted(df['Banco'].dropna().unique()))

# 🎯 Aplicando filtros
df_filtrado = df[
    (df['Data'] >= pd.to_datetime(data_range[0])) &
    (df['Data'] <= pd.to_datetime(data_range[1])) &
    (df['Mês'].isin(meses)) &
    (df['Ano'].isin(anos)) &
    (df['Pessoa'].isin(pessoas)) &
    (df['Tipo'].isin(tipos)) &
    (df['Banco'].isin(bancos))
]

# 🧮 2. KPIs
total_gastos = df_filtrado['Valor'].sum()
media_diaria = df_filtrado.groupby('Data')['Valor'].sum().mean()

gastos_por_pessoa = df_filtrado.groupby('Pessoa')['Valor'].sum().sort_values(ascending=False)
maior_categoria = df_filtrado.groupby('Tipo')['Valor'].sum().sort_values(ascending=False).head(1)

gasto_medio = df_filtrado['Valor'].mean()
gastos_excessivos = df_filtrado[df_filtrado['Valor'] > 2 * gasto_medio]
qtde_excessivos = len(gastos_excessivos)
valor_excessivo = gastos_excessivos['Valor'].sum()

# KPIs - Layout em colunas
st.markdown("## 📊 Visão Geral")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💵 Total de Gastos", f"R$ {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("📈 Média Diária", f"R$ {media_diaria:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("⚠️ Gastos Excessivos", f"{qtde_excessivos} transações")
col4.metric("💣 Valor Excessivo", f"R$ {valor_excessivo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
if not maior_categoria.empty:
    tipo, valor = maior_categoria.index[0], maior_categoria.iloc[0]
    col5.metric("🏆 Maior Categoria", f"{tipo} - R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# 👤 Gastos por Pessoa
st.subheader("👤 Gastos por Pessoa")
st.bar_chart(gastos_por_pessoa)

# 📉 Gráficos Interativos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Gastos por Categoria")
    fig1 = px.pie(df_filtrado, names="Tipo", values="Valor", title="Distribuição por Tipo de Despesa")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📅 Evolução Diária dos Gastos")
    gastos_diarios = df_filtrado.groupby('Data')['Valor'].sum().reset_index()
    fig2 = px.line(gastos_diarios, x='Data', y='Valor', title="Evolução dos Gastos Diários")
    st.plotly_chart(fig2, use_container_width=True)

# 📊 Comparativo por Banco e Pessoa
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏦 Gastos por Banco")
    fig3 = px.bar(df_filtrado, x='Banco', y='Valor', color='Banco', title="Gastos por Banco", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("👥 Comparativo por Pessoa")
    fig4 = px.bar(df_filtrado, x='Pessoa', y='Valor', color='Pessoa', title="Gastos por Pessoa", barmode="group")
    st.plotly_chart(fig4, use_container_width=True)

# 📆 Mapa de Calor - Gastos por Dia da Semana
st.subheader("🔥 Mapa de Calor - Gastos por Dia da Semana")
df_heat = df_filtrado.copy()
df_heat['Dia da Semana'] = pd.Categorical(df_heat['Dia da Semana'],
    categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    ordered=True
)
heatmap_data = df_heat.groupby(['Dia da Semana'])['Valor'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
fig5 = px.bar(x=heatmap_data.index, y=heatmap_data.values, labels={'x': 'Dia da Semana', 'y': 'Valor'})
st.plotly_chart(fig5, use_container_width=True)

# 🧾 4. Tabela Detalhada
st.subheader("📋 Tabela Detalhada de Gastos")
df_exibicao = df_filtrado[['Data', 'Pessoa', 'Tipo', 'Banco', 'Descrição', 'Valor']].sort_values(by='Data', ascending=False)

# Destaque de gastos acima da média
def destaque(val):
    return 'background-color: #ffcccc' if val > 2 * gasto_medio else ''

st.dataframe(df_exibicao.style.applymap(destaque, subset=['Valor']), use_container_width=True)
