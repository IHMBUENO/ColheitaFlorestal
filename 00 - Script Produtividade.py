import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
    
df1 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/01 colheita_jan_2023.xlsx")
df2 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/02 colheita_fev_2023.xlsx")
df3 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/03 colheita_mar_2023.xlsx")
df4 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/04 colheita_abr_2023.xlsx")
df5 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/05 colheita_mai_2023.xlsx")
df6 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/06 colheita_jun_2023.xlsx")
df7 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/07 colheita_jul_2023.xlsx")
df8 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/08 colheita_ago_2023.xlsx")
df9 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/09 colheita_set_2023.xlsx")
df10 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/10 colheita_out_2023.xlsx")
df11 = pd.read_excel("//brtlgwvfs01eld/florestal/01. PLANEJAMENTO/03. CONTROLE/00. BASE DE DADOS/01. SGF_MANUAL/14. RELATORIO COLHEITA NOVO/2023/11 colheita_nov_2023.xlsx")

df_prod = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11])

df_prod["Dia"] = df_prod['Data Operação'].dt.day
df_prod["Mês"] = df_prod['Data Operação'].dt.month
df_prod['Mês Nome'] = df_prod['Data Operação'].dt.strftime('%B')
df_prod['Mês - Ano'] = df_prod['Data Operação'].dt.strftime('%B-%Y')
df_prod['Ano'] = df_prod['Data Operação'].dt.year
df_prod['Tip Parada'].fillna("Operando", inplace=True)
df_prod=df_prod[df_prod['Tip Parada'] == "Operando"]
df_prod=df_prod[df_prod['Vlr Volume Apontado'] > 0]
df_prod=df_prod.loc[(df_prod['Cd Operação']== 'Baldeio Forwarder')|
                    (df_prod['Cd Operação']== 'Corte Harvester')]


df_prod = df_prod.groupby(['Fazenda', 'Data Operação', 'Dia', 'Mês','Mês Nome','Mês - Ano','Ano',
                   'Projeto', 'Talhão', 'Dcr Atividade', 'Cd Operação','Dcr Frente Operação',
                   'Dcr Funcionário Operador','Tip Parada']).agg({
                   'Vlr Volume Apontado':'sum',
                   'Vlr Volume Ajustado':'sum',
                   'Vlr Volume Eficiência':'sum',
                   'Vol. Untário':'mean',
                   'Qtd Duração':'sum'  
                   }).reset_index().rename(columns={
                   'Dcr Funcionário Operador':'Operador',
                   'Cd Operação':'Operação',
                   'Vol. Untário':"VMI (m³)"                
                   })

df_prod['Produtividade'] = df_prod['Vlr Volume Apontado']/df_prod['Qtd Duração']

df_prod.to_excel('Producao Colheita.xlsx', index=False)
                   
