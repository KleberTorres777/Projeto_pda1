import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')
st.title('Dashboard de Análise de Dados :bar_chart:')

def formata_numero(valor, prefixo=''):
    for unidade in ['', ' mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

np.random.seed(23)

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

# Média salarial por cidade
salario_cidades = dados.groupby('Cidade')[['Salario']].mean().reset_index().sort_values('Salario', ascending=False)

# Média salarial por profissão
salario_profissoes = dados.groupby('Profissao')[['Salario']].mean().reset_index().sort_values('Salario', ascending=False)

# Distribuição por nível de escolaridade
escolaridade_distribuicao = dados['Nivel_Escolaridade'].value_counts().reset_index()
escolaridade_distribuicao.columns = ['Nivel_Escolaridade', 'Quantidade']

# Gráfico de barras para média salarial por cidade
fig_salario_cidades = px.bar(
    salario_cidades,
    x='Cidade',
    y='Salario',
    text_auto=True,
    title='Média Salarial por Cidade'
)

# Gráfico de barras para média salarial por profissão
fig_salario_profissoes = px.bar(
    salario_profissoes,
    x='Profissao',
    y='Salario',
    text_auto=True,
    title='Média Salarial por Profissão'
)

# Gráfico de pizza para nível de escolaridade
fig_escolaridade = px.pie(
    escolaridade_distribuicao,
    names='Nivel_Escolaridade',
    values='Quantidade',
    title='Distribuição por Nível de Escolaridade'
)

aba1, aba2, aba3 = st.tabs(['Análise Salarial', 'Pontuação dos Clientes', 'Distribuição Escolaridade'])

with aba1:
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric('Média Salarial Geral', formata_numero(dados['Salario'].mean(), 'R$'))
        st.plotly_chart(fig_salario_cidades, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de Registros', dados.shape[0])
        st.plotly_chart(fig_salario_profissoes, use_container_width=True)

with aba2:
    st.metric('Média de Pontuação', f"{dados['Pontuacao_Cliente'].mean():.2f}")
    st.metric('Pontuação Máxima', dados['Pontuacao_Cliente'].max())
    st.metric('Pontuação Mínima', dados['Pontuacao_Cliente'].min())
    st.dataframe(dados[['Nome', 'Pontuacao_Cliente']])
    
with aba3:
    st.plotly_chart(fig_escolaridade, use_container_width=True)
