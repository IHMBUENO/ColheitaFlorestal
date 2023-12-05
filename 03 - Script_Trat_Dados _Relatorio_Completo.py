import pandas as pd
import numpy as np
import datetime
import time
import plotly.express as px
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")    
import streamlit as st
import altair as alt
import os 
from PIL import Image
import plotly

### ======================================================================================
## ----------------------------------------------------- Importando todos os dados
### ======================================================================================

# Diretório onde estão os arquivos
diretorio = r'Y:\00. BASE DE DADOS\01. SGF_MANUAL\14. RELATORIO COLHEITA NOVO\2023'

# Lista para armazenar os DataFrames de cada arquivo
dataframes = []
ano = 2023
    # Loop pelos meses
for mes in range(1, 13):
        numero_mes_formatado = f'{mes:02d}'
        nome_arquivo = f'{ano}.{numero_mes_formatado} - BASE COLHEITA NOVO.xlsx'

        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

        print(f'Tentando ler o arquivo: {caminho_arquivo}')

        if os.path.exists(caminho_arquivo):
            df = pd.read_excel(caminho_arquivo)
            dataframes.append(df)
            print(f'Arquivo {nome_arquivo} lido com sucesso.')
        else:
            print(f'Arquivo {nome_arquivo} não encontrado.')

# Verifica se há DataFrames na lista antes de tentar concatenar
if dataframes:
    # Concatena todos os DataFrames em um único DataFrame
    df_final = pd.concat(dataframes, ignore_index=True)
    # Exibe o DataFrame final
    print(df)
else:
    print('Nenhum arquivo encontrado. Verifique os caminhos e nomes dos arquivos.')


### ==============================================================================================
## ----------------------------------------------------- FILTRANDO AS INFORMAÇÕES DE PRODUTIVIDADE
### ==============================================================================================

#Filtrando Coordenação Celulose
df_produtividade = df_final[(df_final['Dcr Atividade'] == "Baldeio")|(df_final['Dcr Atividade'] == "Corte")]

# Filtrando Apenas as Horas Trabalhadas
#df_produtividade = df_produtividade[(df_produtividade['Tip Parada'] == 0)]

# Extraindo o Mês
df_produtividade['Mês'] = df_produtividade['Data Operação'].dt.month_name()

# Extraindo o Ano
df_produtividade['Ano'] = df_produtividade['Data Operação'].dt.year

### Selecionando a fProdutividade
fProdutividade = df_produtividade.groupby(["Ano","Mês","Data Operação", "Fazenda", "Projeto", "Talhão","Cd Operação",
                                         'Dcr Frente Operação','Dcr Funcionário Operador','Dcr Equipamento','Abrev Turno']).agg(
    {"Vlr Area":"mean",
     "Vlr Volume Apontado":"sum",
     "Vlr Volume Ajustado":"sum",
     "Vlr Volume Eficiência":"sum",
     "Qtd Duração":"sum",
     "Vol. Untário":"mean"}
).reset_index()
                                        
### Filtrando Volume Apontado Maior que                                        
fProdutividade = fProdutividade[(fProdutividade["Vlr Volume Apontado"] >0) | (fProdutividade["Qtd Duração"] > 0)]

### Calculando a Produtividade
fProdutividade['Produtividade (m³/h)'] = fProdutividade['Vlr Volume Apontado']/fProdutividade["Qtd Duração"]

### Selecionando a Produtividade Maior que 0
fProdutividade=fProdutividade[fProdutividade['Produtividade (m³/h)']>0]

## Exportando dados
fProdutividade.to_excel("fProdutividade.xlsx", index=False)

### ==============================================================================================
## ----------------------------------------------------- FILTRANDO AS INFORMAÇÕES DE DM e EO
### ==============================================================================================

df_final['Grupo de Ajuste'].fillna("OP", inplace=True)
df_final['Tip Parada'].fillna("Operando", inplace=True)

df_relogio = df_final.groupby(['Data Operação','Fazenda','Dcr Atividade', 'Cd Operação', 'Dcr Frente Operação', 'Dcr Equipamento',
                         'Abrev Turno','Num Horas Turno','Tip Parada']).agg({'Qtd Duração':'sum'
                                                                           }).reset_index()

df_relogio =  pd.pivot_table(df_relogio, index=['Data Operação','Fazenda' ,'Dcr Atividade', 'Cd Operação',
                                                'Dcr Frente Operação', 'Dcr Equipamento', 'Abrev Turno',
                                                'Num Horas Turno'],
                     columns= 'Tip Parada',
                     values='Qtd Duração'                       
                     ).fillna(0).reset_index().rename(columns={0:"Operando"})
                       
df_relogio = df_relogio.groupby(["Data Operação","Fazenda" ,"Dcr Atividade","Cd Operação" ,'Dcr Frente Operação']).agg({
    'Num Horas Turno':'sum',
    'Operando':'sum',
    'A':'sum',
    'M':'sum',
    "N":'sum',
    'O':'sum'
}).reset_index()

df_relogio['DM'] = 'NA'
df_relogio['EO'] = 'NA'
df_relogio['TU'] = 'NA'

for i in range(len(df_relogio)):
    df_relogio['DM'][i] = round(1 - (df_relogio['M'][i] / (df_relogio['Operando'][i] + df_relogio['O'][i])),2)
    df_relogio['EO'][i] = round(1 - (df_relogio['O'][i]/(df_relogio['Operando'][i]+df_relogio['O'][i])),2)
    df_relogio['TU'][i] = round(df_relogio['DM'][i]*df_relogio['EO'][i],2)
    


df_relogio.fillna(0, inplace=True)

df_relogio.to_excel('fhorimetro.xlsx')






