import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(layout='wide')

# Função para carregar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv('Bike_rent.csv')
    df['dteday'] = pd.to_datetime(df['dteday'], format='%d-%m-%Y')
    return df

dados = carregar_dados()

# Sidebar
st.sidebar.title('Filtros')

# Filtro por condição climática
climas = dados['weathersit'].unique()
filtro_clima = st.sidebar.multiselect('Condição climática', climas, default=climas)
dados_filtrados = dados[dados['weathersit'].isin(filtro_clima)]

# Filtro por temperatura
temp_min, temp_max = st.sidebar.slider('Temperatura (°C)', float(dados['temp'].min()), float(dados['temp'].max()), (float(dados['temp'].min()), float(dados['temp'].max())))
dados_filtrados = dados_filtrados[(dados_filtrados['temp'] >= temp_min) & (dados_filtrados['temp'] <= temp_max)]

# 🔍 ANÁLISE EXPLORATÓRIA
st.sidebar.subheader("Análise Exploratória 📊")

# Estatísticas descritivas
st.subheader("📌 Estatísticas Descritivas")
st.write(dados_filtrados[['temp', 'hum', 'windspeed', 'cnt']].describe())

# Métricas principais
media_temp = dados_filtrados['temp'].mean()
mediana_temp = dados_filtrados['temp'].median()
desvio_temp = dados_filtrados['temp'].std()
total_alugueis = dados_filtrados['cnt'].sum()

# Exibir métricas no Streamlit
st.metric('Temperatura Média (°C)', f"{media_temp:.2f}")
st.metric('Mediana da Temperatura (°C)', f"{mediana_temp:.2f}")
st.metric('Desvio Padrão da Temperatura (°C)', f"{desvio_temp:.2f}")
st.metric('Total de Aluguéis', total_alugueis)

# Gráficos exploratórios
fig_alugueis_tempo = px.line(dados_filtrados, x='dteday', y='cnt', title='Evolução do número de aluguéis')
fig_alugueis_clima = px.box(dados_filtrados, x='weathersit', y='cnt', title='Distribuição de aluguéis por condição climática')
fig_alugueis_temp = px.scatter(dados_filtrados, x='temp', y='cnt', title='Relação entre temperatura e número de aluguéis')

# Exibição dos gráficos
st.title('Dashboard de Aluguel de Bicicletas 🚴‍♂️')
st.plotly_chart(fig_alugueis_tempo, use_container_width=True)
st.plotly_chart(fig_alugueis_clima, use_container_width=True)
st.plotly_chart(fig_alugueis_temp, use_container_width=True)

# Download dos dados filtrados
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(dados_filtrados)
st.download_button('Baixar dados filtrados', csv, 'dados_filtrados.csv', 'text/csv')
