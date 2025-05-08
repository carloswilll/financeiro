import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Meu Painel Financeiro Pessoal", layout="wide")

st.title("💰 Meu Painel Financeiro Pessoal")

# Upload de Arquivo com key variável para evitar erro de sessão
import time
key_unique = f"uploader_{int(time.time())}"
uploaded_file = st.file_uploader("📁 Faça upload do arquivo (.csv ou .xlsx)", type=["csv", "xlsx"], key=key_unique)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error("Erro ao ler o arquivo. Verifique se está no formato correto.")
        st.stop()

    # Pré-processamento
    df.columns = df.columns.str.strip().str.lower()
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df.dropna(subset=['data'], inplace=True)
    df['ano_mes'] = df['data'].dt.to_period('M').astype(str)
    df['dia_semana'] = df['data'].dt.day_name()

    # Filtros
    with st.sidebar:
        st.header("🔍 Filtros")
        data_min = df['data'].min()
        data_max = df['data'].max()

        data_range = st.date_input("Período", [data_min, data_max])
        pessoas = st.multiselect("Pessoa", options=df['pessoa'].unique(), default=df['pessoa'].unique())
        tipos = st.multiselect("Tipo de Despesa", options=df['tipo'].unique(), default=df['tipo'].unique())
        bancos = st.multiselect("Banco", options=df['banco'].unique(), default=df['banco'].unique())

    # Aplicando filtros
    df_filtrado = df[
        (df['data'] >= pd.to_datetime(data_range[0])) &
        (df['data'] <= pd.to_datetime(data_range[1])) &
        (df['pessoa'].isin(pessoas)) &
        (df['tipo'].isin(tipos)) &
        (df['banco'].isin(bancos))
    ]

    # KPIs
    total = df_filtrado['valor'].sum()
    media_dia = df_filtrado.groupby('data')['valor'].sum().mean()
    gastos_por_pessoa = df_filtrado.groupby('pessoa')['valor'].sum()
    maior_categoria = df_filtrado.groupby('descricao')['valor'].sum().idxmax()
    valor_maior_categoria = df_filtrado.groupby('descricao')['valor'].sum().max()

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total de Gastos", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("📅 Média Diária", f"R$ {media_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("🏷️ Maior Categoria", f"{maior_categoria} - R$ {valor_maior_categoria:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Gastos por pessoa
    st.subheader("👥 Gastos por Pessoa")
    st.dataframe(gastos_por_pessoa.reset_index().rename(columns={"valor": "Total (R$)"}))

    # Gráficos
    st.subheader("📊 Análises Visuais")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(df_filtrado, names="tipo", values="valor", title="Distribuição por Tipo de Despesa")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(df_filtrado.groupby('banco')['valor'].sum().reset_index(), x='banco', y='valor',
                      title="Gasto por Banco", text_auto=True)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(df_filtrado.groupby('data')['valor'].sum().reset_index(), x='data', y='valor',
                   title="Evolução Diária dos Gastos")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.density_heatmap(df_filtrado, x="dia_semana", y=df_filtrado["data"].dt.day, z="valor", histfunc="sum",
                              title="Mapa de Calor de Gastos por Dia da Semana")
    st.plotly_chart(fig4, use_container_width=True)

    # Tabela Detalhada
    st.subheader("📋 Tabela Detalhada de Gastos")
    styled_df = df_filtrado.style.applymap(
        lambda v: 'background-color: #ffcccc' if v > df_filtrado['valor'].mean() else ''
        if isinstance(v, (int, float)) else '', subset=['valor']
    )
    st.dataframe(styled_df, use_container_width=True)

else:
    st.info("Por favor, carregue um arquivo .csv ou .xlsx para iniciar o dashboard.")

