import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv('Bike_rent.csv')  # Substituir pelo caminho real
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

dados = carregar_dados()

def formata_numero(valor):
    return f'{valor:,.0f}'.replace(',', '.')

st.title('DASHBOARD DE ALUGUEL DE BICICLETAS 🚴‍♂️')

# Filtros
st.sidebar.title('Filtros')
clima = st.sidebar.multiselect('Condições Climáticas', dados['weather'].unique(), default=dados['weather'].unique())
usuario = st.sidebar.multiselect('Tipo de Usuário', dados['user_type'].unique(), default=dados['user_type'].unique())
intervalo_horas = st.sidebar.slider('Horário do Dia', 0, 23, (0, 23))

dados_filtrados = dados[
    (dados['weather'].isin(clima)) &
    (dados['user_type'].isin(usuario)) &
    (dados['hour'].between(intervalo_horas[0], intervalo_horas[1]))
]

# Métricas
st.metric('Total de Aluguéis', formata_numero(dados_filtrados['count'].sum()))

# Gráficos
fig_alugueis_horario = px.line(dados_filtrados.groupby('hour')['count'].sum().reset_index(), 
                               x='hour', y='count', markers=True, title='Aluguéis por Hora')

fig_temp_impacto = px.scatter(dados_filtrados, x='temp', y='count', title='Impacto da Temperatura nos Aluguéis', trendline='ols')

fig_alugueis_semana = px.bar(dados_filtrados.groupby('weekday')['count'].sum().reset_index(), 
                              x='weekday', y='count', title='Aluguéis por Dia da Semana')

# Layout
st.plotly_chart(fig_alugueis_horario, use_container_width=True)
st.plotly_chart(fig_temp_impacto, use_container_width=True)
st.plotly_chart(fig_alugueis_semana, use_container_width=True)

# Baixar dados filtrados
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(dados_filtrados)
st.download_button('Baixar Dados Filtrados', csv, 'dados_filtrados.csv', 'text/csv')
