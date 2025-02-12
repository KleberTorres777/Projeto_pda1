import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

np.random.seed(23)  # Garante que os dados gerados sejam reprodutíveis

dados = {
    'Nome': ['João', 'Maria', 'Yago', 'Ana', 'Lucas', 'Beatriz', 'Fernanda', 'Rafael', 'Patricia', 'Gabriel',
             'Camila', 'Pedro', 'Isabela', 'Mateus', 'Julia', 'Rodrigo', 'Mariana', 'Felipe', 'Leticia', 'Vinicius',
             'Amanda', 'Eduardo', 'Larissa', 'Guilherme', 'Tatiane', 'Henrique', 'Natasha', 'José', 'Carla', 'Thiago',
             'Lais', 'Bruno', 'Aline', 'Renato', 'Andreia', 'Diego', 'Fernanda', 'Leandro', 'Cristiane', 'Chico'],
    'Idade': np.random.randint(18, 90, size=40),
    'Genero': np.random.choice(['Masculino', 'Feminino'], size=40),
    'Profissao': np.random.choice(['Estudante', 'Profissional', 'Empresario'], size=40),
    'Cidade': np.random.choice(['Santarem', 'Oriximina', 'Belem'], size=40),
    'Salario': np.random.uniform(2000, 10000, size=40),
    'Nivel_Escolaridade': np.random.choice(['Ensino Médio', 'Graduação', 'Pós-Graduação'], size=40),
    'Pontuacao_Cliente': np.random.randint(1, 101, size=40)
}

dados = pd.DataFrame(dados)

st.set_page_config(layout='wide')
st.title('Dashboard de Análise de Dados :bar_chart:')

def formata_numero(valor, prefixo=''):
    for unidade in ['', ' mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

salario_cidades = dados.groupby('Cidade')[['Salario']].mean().reset_index().sort_values('Salario', ascending=False)
salario_profissoes = dados.groupby('Profissao')[['Salario']].mean().reset_index().sort_values('Salario', ascending=False)

# Média Salarial por Cidade
fig_mapa_salarios = px.bar(
    salario_cidades, x='Cidade', y='Salario', title='Média Salarial por Cidade',
    color='Cidade', text=salario_cidades['Salario'].apply(lambda x: f'R$ {x:,.2f}'),
    labels={'Salario': 'Média Salarial', 'Cidade': 'Cidade'}
)
fig_mapa_salarios.update_layout(yaxis_title='Média Salarial')

# Média Salarial por Profissão
fig_salario_profissoes = px.bar(
    salario_profissoes, x='Profissao', y='Salario', title='Média Salarial por Profissão',
    color='Profissao', text=salario_profissoes['Salario'].apply(lambda x: f'R$ {x:,.2f}'),
    labels={'Salario': 'Média Salarial', 'Profissao': 'Profissão'}
)
fig_salario_profissoes.update_layout(yaxis_title='Média Salarial')

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric('Média Salarial Geral', formata_numero(dados['Salario'].mean(), 'R$'))
    st.plotly_chart(fig_mapa_salarios, use_container_width=True)

with coluna2:
    st.metric('Número de Registros', dados.shape[0])
    st.plotly_chart(fig_salario_profissoes, use_container_width=True)
    
    st.dataframe(dados)
