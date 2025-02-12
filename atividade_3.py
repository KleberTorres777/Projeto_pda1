import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Configuração da página
st.set_page_config(layout='wide')

# Função para formatar números
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil', 'milhões', 'bilhões']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'.strip()
        valor /= 1000
    return f'{prefixo} {valor:.2f} trilhões'

# Função para converter DataFrame em CSV
@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para exibir mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

# Página 1: Dados Brutos
def pagina_dados_brutos():
    st.title('DADOS BRUTOS')

    url = 'https://labdados.com/produtos'
    response = requests.get(url)
    dados = pd.DataFrame.from_dict(response.json())
    dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

    with st.expander('Colunas'):
        colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

    # Configuração dos filtros
    st.sidebar.title('Filtros')

    data_min = dados['Data da Compra'].min()
    data_max = dados['Data da Compra'].max()
    if pd.isna(data_min) or pd.isna(data_max):
        data_min, data_max = pd.Timestamp("2020-01-01"), pd.Timestamp.today()

    filtros = {
        "produtos": st.sidebar.multiselect('Nome do produto', dados['Produto'].unique(), dados['Produto'].unique()),
        "categoria": st.sidebar.multiselect('Categoria do produto', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique()),
        "preco": st.sidebar.slider('Preço do produto', 0, 5000, (0, 5000)),
        "frete": st.sidebar.slider('Frete da venda', 0, 250, (0, 250)),
        "data_compra": st.sidebar.date_input('Data da compra', (data_min, data_max)),
        "vendedores": st.sidebar.multiselect('Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique()),
        "local_compra": st.sidebar.multiselect('Local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique()),
        "avaliacao": st.sidebar.slider('Avaliação da compra', 1, 5, (1, 5)),
        "tipo_pagamento": st.sidebar.multiselect('Tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique()),
        "qtd_parcelas": st.sidebar.slider('Quantidade de parcelas', 1, 24, (1, 24))
    }

    query = ' & '.join([
        "Produto in @filtros['produtos']" if filtros['produtos'] else "Produto == Produto",
        "`Categoria do Produto` in @filtros['categoria']" if filtros['categoria'] else "`Categoria do Produto` == `Categoria do Produto`",
        f"{filtros['preco'][0]} <= Preço <= {filtros['preco'][1]}",
        f"{filtros['frete'][0]} <= Frete <= {filtros['frete'][1]}",
        f"`Data da Compra` >= @filtros['data_compra'][0] and `Data da Compra` <= @filtros['data_compra'][1]",
        "Vendedor in @filtros['vendedores']" if filtros['vendedores'] else "Vendedor == Vendedor",
        "`Local da compra` in @filtros['local_compra']" if filtros['local_compra'] else "`Local da compra` == `Local da compra`",
        f"{filtros['avaliacao'][0]} <= `Avaliação da compra` <= {filtros['avaliacao'][1]}",
        "`Tipo de pagamento` in @filtros['tipo_pagamento']" if filtros['tipo_pagamento'] else "`Tipo de pagamento` == `Tipo de pagamento`",
        f"{filtros['qtd_parcelas'][0]} <= `Quantidade de parcelas` <= {filtros['qtd_parcelas'][1]}"
    ])

    dados_filtrados = dados.query(query)
    dados_filtrados = dados_filtrados[colunas]

    st.dataframe(dados_filtrados)
    st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

    # Download CSV
    st.markdown('Escreva um nome para o arquivo')
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados.csv')
    with coluna2:
        if not dados_filtrados.empty:
            st.download_button(
                'Fazer o download da tabela em csv',
                data=converte_csv(dados_filtrados),
                file_name=nome_arquivo,
                mime='text/csv',
                on_click=mensagem_sucesso
            )
        else:
            st.warning("Nenhum dado disponível para download.")

# Página 2: Dashboard
def pagina_dashboard():
    st.title('DASHBOARD DE VENDAS :shopping_trolley:')

    url = 'https://labdados.com/produtos'
    regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

    st.sidebar.title('Filtros')
    regiao = st.sidebar.selectbox('Região', regioes)
    regiao = '' if regiao == 'Brasil' else regiao.lower()

    todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
    ano = '' if todos_anos else st.sidebar.slider('Ano', 2020, 2023)

    query_string = {'regiao': regiao, 'ano': ano}
    response = requests.get(url, params=query_string)
    dados = pd.DataFrame.from_dict(response.json())
    dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

    st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

    # Métricas
    receita_total = formata_numero(dados['Preço'].sum(skipna=True), 'R$')
    total_vendas = formata_numero(dados.shape[0])

    st.metric('Receita', receita_total)
    st.metric('Quantidade de vendas', total_vendas)

# Menu de navegação
pagina = st.sidebar.selectbox('Selecione a página', ['Dados Brutos', 'Dashboard'])

if pagina == 'Dados Brutos':
    pagina_dados_brutos()
else:
    pagina_dashboard()