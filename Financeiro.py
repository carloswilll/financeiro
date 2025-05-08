import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

st.set_page_config(page_title="Meu Painel Financeiro Pessoal", layout="wide")
st.title("📊 Meu Painel Financeiro Pessoal")

uploaded_file = st.file_uploader("Selecione um arquivo (.csv ou .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            content = uploaded_file.read().decode("latin-1")
            sep = ";" if ";" in content.splitlines()[0] else ","
            df = pd.read_csv(io.StringIO(content), sep=sep)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = [col.strip() for col in df.columns]
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        df.dropna(subset=["Data"], inplace=True)

        df["Ano"] = df["Data"].dt.year
        df["Mês"] = df["Data"].dt.month
        df["Dia da Semana"] = df["Data"].dt.day_name()

        st.sidebar.header("🔍 Filtros")
        data_ini, data_fim = st.sidebar.date_input("Intervalo de Datas", [df["Data"].min(), df["Data"].max()])

        pessoas = st.sidebar.multiselect("Pessoa", options=df["Pessoa"].unique(), default=df["Pessoa"].unique())
        tipos = st.sidebar.multiselect("Tipo de Despesa", options=df["Tipo"].unique(), default=df["Tipo"].unique())
        bancos = st.sidebar.multiselect("Banco", options=df["Banco"].unique(), default=df["Banco"].unique())

        df_filtrado = df[(df["Data"] >= pd.to_datetime(data_ini)) & (df["Data"] <= pd.to_datetime(data_fim))]
        df_filtrado = df_filtrado[df_filtrado["Pessoa"].isin(pessoas)]
        df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipos)]
        df_filtrado = df_filtrado[df_filtrado["Banco"].isin(bancos)]

        # KPIs
        total_gasto = df_filtrado["Valor"].sum()
        dias = (df_filtrado["Data"].max() - df_filtrado["Data"].min()).days + 1
        media_diaria = total_gasto / dias if dias else 0
        maior_categoria = df_filtrado.groupby("Tipo")["Valor"].sum().idxmax()
        maior_valor_categoria = df_filtrado.groupby("Tipo")["Valor"].sum().max()
        gasto_por_pessoa = df_filtrado.groupby("Pessoa")["Valor"].sum().to_dict()
        media_total = df_filtrado["Valor"].mean()
        gastos_excessivos = df_filtrado[df_filtrado["Valor"] > media_total]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 Total Gasto", f"R$ {total_gasto:,.2f}")
        col2.metric("📆 Média Diária", f"R$ {media_diaria:,.2f}")
        col3.metric("🚨 Gastos Excessivos", f"{len(gastos_excessivos)} itens")
        col4.metric("🏷️ Maior Categoria", f"{maior_categoria} - R$ {maior_valor_categoria:,.2f}")
        col5.metric("👥 Pessoas", ", ".join([f"{p}: R$ {v:,.2f}" for p, v in gasto_por_pessoa.items()]))

        # Gráficos
        st.subheader("📈 Análises Visuais")
        col1, col2 = st.columns(2)

        with col1:
            fig_pizza = px.pie(df_filtrado, names="Tipo", values="Valor", title="Distribuição por Tipo de Despesa")
            st.plotly_chart(fig_pizza, use_container_width=True)

        with col2:
            fig_bar = px.bar(df_filtrado, x="Pessoa", y="Valor", color="Pessoa", title="Gastos por Pessoa")
            st.plotly_chart(fig_bar, use_container_width=True)

        fig_linha = px.line(df_filtrado.sort_values("Data"), x="Data", y="Valor", title="Evolução Diária dos Gastos")
        st.plotly_chart(fig_linha, use_container_width=True)

        fig_calor = px.density_heatmap(df_filtrado, x="Dia da Semana", y="Pessoa", z="Valor",
                                       histfunc="sum", title="Mapa de Calor dos Gastos")
        st.plotly_chart(fig_calor, use_container_width=True)

        # Tabela
        st.subheader("📋 Tabela Detalhada")
        df_formatado = df_filtrado.copy()
        df_formatado["Valor"] = df_formatado["Valor"].map(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df_formatado.reset_index(drop=True), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("📁 Envie um arquivo .csv ou .xlsx para iniciar a análise.")

