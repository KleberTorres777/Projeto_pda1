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

st.title('Dashboard de Vendas :shopping_trolley:')

url = 'https://labdados.com/produtos'

# Requisição de dados
response = requests.get(url)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    try:
        dados = pd.DataFrame.from_dict(response.json())
        
        # Verificar se os dados possuem o formato esperado
        if dados.empty:
            st.error('Dados retornados vazios.')
        else:
            # Conversão da data
            dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

            # Tabelas
            receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
            receita_estados = dados.drop_duplicates(subset='Local da compra') \
                [['Local da compra', 'lat', 'lon']] \
                .merge(receita_estados, left_on='Local da compra', right_index=True) \
                .sort_values('Preço', ascending=False)

            # Receita mensal
            receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
            receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
            receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

            # Receita por categoria
            receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

            # Gráficos
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

            # Visualização no Streamlit
            coluna1, coluna2 = st.columns(2)
            with coluna1:
                st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
                st.plotly_chart(fig_mapa_receita, use_container_width=True)
                st.plotly_chart(fig_receita_estados, use_container_width=True)

            with coluna2:
                st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
                st.plotly_chart(fig_receita_mensal, use_container_width=True)
                st.plotly_chart(fig_receita_categorias, use_container_width=True)

            st.dataframe(dados)

    except Exception as e:
        st.error(f'Ocorreu um erro ao processar os dados: {e}')
else:
    st.error(f'Erro na requisição: {response.status_code}. Verifique a URL ou a API.')

