import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Análise Financeira")

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione o arquivo CSV", type="csv")

if uploaded_file is not None:
    # Leitura do arquivo
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")

        # Conversão da coluna de data, se existir
        if "Data" in df.columns:
            df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")

        # Exibe os dados
        st.subheader("Prévia dos Dados")
        st.dataframe(df)

        # Exemplo de estatísticas
        if "Valor a Pagar" in df.columns:
            st.subheader("Resumo dos Valores a Pagar")
            st.metric("Total", f'R$ {df["Valor a Pagar"].sum():,.2f}')
            st.metric("Média", f'R$ {df["Valor a Pagar"].mean():,.2f}')
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo CSV.")


# Tratamento de dados
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
df["Valor"] = df["Valor"].replace("R\$ ", "", regex=True).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
df["Ano"] = df["Data"].dt.year
df["Mês"] = df["Data"].dt.strftime('%B')
df["Dia da Semana"] = df["Data"].dt.day_name()

# Sidebar - Filtros
st.sidebar.header("Filtros")
data_inicio = st.sidebar.date_input("Data Início", df["Data"].min())
data_fim = st.sidebar.date_input("Data Fim", df["Data"].max())
grupo = st.sidebar.multiselect("Grupo de Pessoas", options=df["Grupo de Dias"].unique(), default=df["Grupo de Dias"].unique())
tipo_despesa = st.sidebar.multiselect("Tipo de Despesa", options=df["Tipo de Despesa"].unique(), default=df["Tipo de Despesa"].unique())
banco = st.sidebar.multiselect("Banco", options=df["Banco"].unique(), default=df["Banco"].unique())

# Aplicação dos filtros
df_filtrado = df[
    (df["Data"] >= pd.to_datetime(data_inicio)) &
    (df["Data"] <= pd.to_datetime(data_fim)) &
    (df["Grupo de Dias"].isin(grupo)) &
    (df["Tipo de Despesa"].isin(tipo_despesa)) &
    (df["Banco"].isin(banco))
]

# Cabeçalho
st.title("💰 Meu Painel Financeiro Pessoal")

# KPIs
total = df_filtrado["Valor"].sum()
media_diaria = df_filtrado.groupby("Data")["Valor"].sum().mean()
gastos_por_pessoa = df_filtrado.groupby("Grupo de Dias")["Valor"].sum()
excessivos = df_filtrado[df_filtrado["Gasto Excessivo"] == "Acima da Média"]
maior_categoria = df_filtrado.groupby("Descrição")["Valor"].sum().idxmax()
maior_valor = df_filtrado.groupby("Descrição")["Valor"].sum().max()

st.subheader("📊 Visão Geral")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total de Gastos", f"R$ {total:,.2f}")
col2.metric("📅 Média Diária", f"R$ {media_diaria:,.2f}")
col3.metric("🚨 Gastos Excessivos", f"{len(excessivos)} (R$ {excessivos['Valor'].sum():,.2f})")

for pessoa, valor in gastos_por_pessoa.items():
    st.write(f"👤 {pessoa}: R$ {valor:,.2f}")

st.write(f"🏆 Maior Categoria: {maior_categoria} - R$ {maior_valor:,.2f}")

# Gráficos
st.subheader("📈 Gráficos Interativos")

# Pizza ou barra horizontal: Despesas por categoria
fig1 = px.pie(df_filtrado, names="Descrição", values="Valor", title="Despesas por Descrição")
st.plotly_chart(fig1)

# Linha temporal: Evolução dos gastos por dia
fig2 = px.line(df_filtrado.groupby("Data")["Valor"].sum().reset_index(), x="Data", y="Valor", title="Evolução dos Gastos por Dia")
st.plotly_chart(fig2)

# Gráfico de barras: Comparativo de gastos por banco ou pessoa
fig3 = px.bar(df_filtrado, x="Banco", y="Valor", color="Banco", title="Gastos por Banco", barmode="group")
st.plotly_chart(fig3)

fig4 = px.bar(df_filtrado, x="Grupo de Dias", y="Valor", color="Grupo de Dias", title="Gastos por Pessoa", barmode="group")
st.plotly_chart(fig4)

# Mapa de calor: Gastos por dia da semana
heatmap_data = df_filtrado.groupby("Dia da Semana")["Valor"].sum().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
).reset_index()
fig5 = px.imshow([heatmap_data["Valor"]], labels=dict(x=heatmap_data["Dia da Semana"], color="Valor"), title="Gastos por Dia da Semana")
st.plotly_chart(fig5)

# Tabela detalhada
st.subheader("📋 Tabela Detalhada de Gastos")
df_exibicao = df_filtrado[["Data", "Descrição", "Valor", "Banco", "Tipo de Despesa", "Grupo de Dias", "Gasto Excessivo"]]
st.dataframe(df_exibicao.style.applymap(lambda val: "background-color: #ff9999" if val == "Acima da Média" else "", subset=["Gasto Excessivo"]))

# Observações manuais (extras)
st.subheader("📝 Comentários e Observações")
st.text_area("Anote aqui suas observações do período analisado:")
