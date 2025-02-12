import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuração do layout do Streamlit
st.set_page_config(layout='wide')

def formata_numero(valor, prefixo=''):
    for unidade in ['', ' mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Definição dos filtros na barra lateral
st.sidebar.title('Filtros')

# Filtro por região
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

# Filtro por ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

# URL da API com query string para filtros
url = 'https://labdados.com/produtos'
query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())

# Conversão da data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

# Filtro por vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra') \
    [['Local da compra', 'lat', 'lon']] \
    .merge(receita_estados, left_on='Local da compra', right_index=True) \
    .sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

# Tabelas de Quantidade de Vendas
vendas_estados = dados.groupby('Local da compra')[['Preço']].count().rename(columns={'Preço': 'Quantidade de Vendas'})
vendas_estados = dados.drop_duplicates(subset='Local da compra') \
    [['Local da compra', 'lat', 'lon']] \
    .merge(vendas_estados, left_on='Local da compra', right_index=True) \
    .sort_values('Quantidade de Vendas', ascending=False)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().rename(columns={'Preço': 'Quantidade de Vendas'}) \
    .sort_values('Quantidade de Vendas', ascending=False)

# Tabelas de Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Gráficos de Receita
fig_mapa_receita = px.scatter_geo(
    receita_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Receita por estado'
)

fig_receita_mensal = px.line(
    receita_mensal,
    x='Mes',
    y='Preço',
    markers=True,
    range_y=(0, receita_mensal['Preço'].max()),
    color='Ano',
    line_dash='Ano',
    title='Receita mensal'
)
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(
    receita_estados.head(),
    x='Local da compra',
    y='Preço',
    text_auto=True,
    title='Top estados'
)
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(
    receita_categorias,
    text_auto=True,
    title='Receita por categoria'
)
fig_receita_categorias.update_layout(yaxis_title='Receita')

# Gráficos de Quantidade de Vendas
fig_vendas_estados = px.bar(
    vendas_estados.head(),
    x='Local da compra',
    y='Quantidade de Vendas',
    text_auto=True,
    title='Top estados (Vendas)'
)
fig_vendas_estados.update_layout(yaxis_title='Quantidade de Vendas')

fig_vendas_mensal = px.line(
    vendas_mensal,
    x='Mes',
    y='Preço',
    markers=True,
    range_y=(0, vendas_mensal['Preço'].max()),
    color='Ano',
    line_dash='Ano',
    title='Vendas mensais'
)
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de Vendas')

fig_vendas_categorias = px.bar(
    vendas_categorias,
    text_auto=True,
    title='Vendas por categoria'
)
fig_vendas_categorias.update_layout(yaxis_title='Quantidade de Vendas')

# Visualização no Streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

# Aba Receita
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

# Aba Quantidade de vendas
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Total de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_estados, use_container_width=True)

    with coluna2:
        st.metric('Média de Vendas por Categoria', formata_numero(vendas_categorias['Quantidade de Vendas'].mean()))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

# Aba Vendedores
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
            x='sum',
            y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (receita)'
        )
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
            x='count',
            y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)'
        )
        st.plotly_chart(fig_vendas_vendedores)
