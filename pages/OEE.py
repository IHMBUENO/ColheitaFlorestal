### --------------------------------------------------------------------------------
### ------------------------ Bibliotecas
### ---------------------------------------------------------------------------
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
from PIL import Image
import plotly
from scipy.optimize import curve_fit
import plotly.graph_objects as go

### -------------------------------------------------------------------------------
## --------------------------- DashBoard Colheita
### ------------------------------------------------------------------------------

st.set_page_config(
    page_title="OEE",
    page_icon="&#xF5E2",
    layout='wide',
    initial_sidebar_state="expanded"
)

### -------------------------------------------------------------------------------
### -------------------------- Importando dados
### -------------------------------------------------------------------------------

@st.cache_data
def busca_df():
    df = pd.read_excel("fhorimetro.xlsx")
    return df

df = busca_df()

logo = Image.open('logo_eldorado.png')
logo2 = Image.open('Capa Linkedin.png')

data_inicial = df['Data Operação'].min()
data_final = df['Data Operação'].max()

### -------------------------------------------------------------------------------
### -------------------------- Criar o SideBar
### -------------------------------------------------------------------------------


with st.sidebar:
    st.image(logo, width=290)
    st.subheader("FILTROS - INFORMAÇÕES PRODUTIVIDADE")
    
    fOperacoes = st.multiselect(
        "Selecione a Operação:",
        options=df['Cd Operação'].unique()
    )
    
    fModulo = st.multiselect(
        "Selecione o Módulo:",
        options=df['Dcr Frente Operação'].unique()
    )
    
    st.subheader('Filtros por Data:')
    
    data_inicial = st.date_input('Selecione a data inicial:', data_inicial)
    data_final = st.date_input('Selecione a data final:', data_final)
    data_inicial = np.datetime64(data_inicial)
    data_final = np.datetime64(data_final)
 
### =====================================================================================================
## ----------------------------------- Tabela dados Gerais
### =====================================================================================================

df_filtrado = df.copy()

# Verificar se fOperacoes não está vazio antes de aplicar o filtro
if fOperacoes:
    df_filtrado = df_filtrado.loc[df_filtrado['Cd Operação'].isin(fOperacoes)]
if fModulo:
    df_filtrado = df_filtrado.loc[df_filtrado['Dcr Frente Operação'].isin(fModulo)]
# Verificar se data_inicial e data_final estão definidos antes de aplicar o filtro de datas
if data_inicial and data_final:
    df_filtrado = df_filtrado[(df_filtrado['Data Operação'] >= data_inicial) & (df_filtrado['Data Operação'] <= data_final)]

df_filtrado['Ano'] = df_filtrado['Data Operação'].dt.year
df_filtrado['Mês'] = df_filtrado['Data Operação'].dt.month
df_filtrado["Mês Núm."] = df_filtrado['Data Operação'].dt.month
df_filtrado["Mês-Ano"] = df_filtrado['Data Operação'].dt.strftime('%m-%Y')
df_filtrado = df_filtrado[df_filtrado["TU"] != 0]

df_filtrado=df_filtrado[['Ano',"Mês-Ano",'Mês',"Data Operação",'Fazenda','Dcr Atividade','Cd Operação', 
            'Dcr Frente Operação','Operando','A','M','O','DM', 'EO', 'TU']]

cor_grafico = '#aed581'
altura_grafico = 500

display = st.checkbox('Exibir Dados Diários:')

if display:
    st.write(df_filtrado)

### ===========================================================================================
##  --------------------------------------- DF Graficos
### ===========================================================================================

df_gráfico = df_filtrado.groupby(['Mês-Ano']).agg(
    {   'Operando':'sum',
        'A':'sum',
        'M':'sum',
        'O':'sum'
     }
).reset_index()

df_gráfico['DM'] = 'NA'
df_gráfico['EO'] = 'NA'
df_gráfico['TU'] = 'NA'

for i in range (len(df_gráfico)):
    df_gráfico['DM'][i] = round(1 - (df_gráfico['M'][i] / (df_gráfico['Operando'][i] + df_gráfico['O'][i])),2)
    df_gráfico['EO'][i] = round(1 - (df_gráfico['O'][i]/(df_gráfico['Operando'][i]+df_gráfico['O'][i])),2)
    df_gráfico['TU'][i] = round(df_gráfico['DM'][i]*df_gráfico['EO'][i],2)


df_gráfico['Mês-Ano'] = pd.to_datetime(df_gráfico['Mês-Ano'])    
df_gráfico = df_gráfico.sort_values(by='Mês-Ano')

### --------------------------------------------------------------------------------------
### ---------------------------------- CARDS
### -------------------------------------------------------------------------------------

DM_Media = round(df_gráfico	['DM'].mean()*100,2)
EO_MEDIA = round(df_gráfico['EO'].mean()*100,2)
TAXA_UTILIZACAO = round(df_gráfico['TU'].mean()*100,2)

st.header(':bar_chart: Indicadores OEE')

dist1,dist2,dist3 = st.columns([1,1,1])

with dist1:
    st.write('**DIPONIBILIDADE MECÂNICA:**') ## ** Negrito
    st.info(f"{DM_Media}%")
    
with dist2:
    st.write('**EFICIÊNCIA OPERACIONAL:**')
    st.info(f"{EO_MEDIA}%")
    
with dist3:
     st.write('**TAXA DE UTILIZAÇÃO**')
     st.info(f"{TAXA_UTILIZACAO}%")
     
st.markdown("---")

## ===============================================================================================
## ----------------------------------------- Gráficos Gerais
## ===============================================================================================

### ==========================================================================================
## ----------------------------------------------
## DM
fig1 = go.Figure()

# Adição da linha horizontal
fig1.add_shape(
    type="line",
    x0=df_gráfico['Mês-Ano'].min(),
    x1=df_gráfico['Mês-Ano'].max(),
    y0=0.9,
    y1=0.9,
    line=dict(color="red", width=2)
)

# Adição dos marcadores como pontos no gráfico de linhas
fig1.add_trace(go.Scatter(
    x=df_gráfico['Mês-Ano'],
    y=df_gráfico['DM'],
    mode='markers+lines',
    line=dict(color='green'),
    marker=dict(color='green', size=8),
))

# Atualização do layout
fig1.update_layout(title='Distribuição Mensal - Disponibilidade Mecânica', 
                   showlegend=False,
                   yaxis=dict(range=[0.75, 1])
)


## -----------------------------------------------
## EO

# Atualização para um gráfico de linhas com marcadores
fig2 = go.Figure()

# Adição da linha horizontal
fig2.add_shape(
    type="line",
    x0=df_gráfico['Mês-Ano'].min(),
    x1=df_gráfico['Mês-Ano'].max(),
    y0=0.9,
    y1=0.9,
    line=dict(color="red", width=2)
)

# Adição dos marcadores como pontos no gráfico de linhas
fig2.add_trace(go.Scatter(
    x=df_gráfico['Mês-Ano'],
    y=df_gráfico['EO'],
    mode='markers+lines',
    line=dict(color='green'),
    marker=dict(color='green', size=8),
))

# Atualização do layout
fig2.update_layout(title='Distribuição Mensal - Eficiência Operacional', 
                   showlegend=False,
                   yaxis=dict(range=[0.75, 1])
)


## -----------------------------------------------
## TU
# Atualização para um gráfico de linhas com marcadores

fig3 = go.Figure()

fig3.add_shape(
    type="line",
    x0=df_gráfico['Mês-Ano'].min(),
    x1=df_gráfico['Mês-Ano'].max(),
    y0=0.75,
    y1=0.75,
    line=dict(color="red", width=2)
)

# Adição dos marcadores como pontos no gráfico de linhas
fig3.add_trace(go.Scatter(
    x=df_gráfico['Mês-Ano'],
    y=df_gráfico['TU'],
    mode='markers+lines',
    line=dict(color='green'),
    marker=dict(color='green', size=8),
))

# Atualização do layout
fig3.update_layout(title='Distribuição Mensal - Eficiência Operacional', 
                   showlegend=False,
                   yaxis=dict(range=[0.65, 0.8])
)

### ==============================================================================
### ---------------------------------- DF GRÁFICOS 2

df_gráfico2 = df_filtrado.groupby(['Dcr Frente Operação']).agg(
    {   'Operando':'sum',
        'A':'sum',
        'M':'sum',
        'O':'sum'
     }
).reset_index()

df_gráfico2['DM'] = 'NA'
df_gráfico2['EO'] = 'NA'
df_gráfico2['TU'] = 'NA'

for i in range (len(df_gráfico2)):
    df_gráfico2['DM'][i] = round(1 - (df_gráfico2['M'][i] / (df_gráfico2['Operando'][i] + df_gráfico2['O'][i])),2)
    df_gráfico2['EO'][i] = round(1 - (df_gráfico2['O'][i]/(df_gráfico2['Operando'][i]+df_gráfico2['O'][i])),2)
    df_gráfico2['TU'][i] = round(df_gráfico2['DM'][i]*df_gráfico2['EO'][i],2)
    
### ==========================================================================================
## ----------------------------------------------
## DM

fig4 = alt.Chart(df_gráfico2).mark_bar(
    color='green',
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x=alt.X('DM', title='DM'),  # Adicione a transformação sort aqui
    y=alt.Y('Dcr Frente Operação', title='Dcr Frente Operação', sort='-x'),
    tooltip=['Dcr Frente Operação', 'DM']
).properties(
    height=altura_grafico,
    title='Disponibilidade Mecânica por Módulo'
).configure_axis(grid=False).configure_view(strokeWidth=0)



## EO

fig5 = alt.Chart(df_gráfico2).mark_bar(
    color='green',
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x=alt.X('EO', title='EO'),  # Adicione a transformação sort aqui
    y=alt.Y('Dcr Frente Operação', title='Dcr Frente Operação', sort='-x'),
    tooltip=['Dcr Frente Operação', 'EO']
).properties(
    height=altura_grafico,
    title='Eficiência Operacional por Módulo'
).configure_axis(grid=False).configure_view(strokeWidth=0)



## TU

fig6 = alt.Chart(df_gráfico2).mark_bar(
    color='green',
    cornerRadiusTopLeft=9,
    cornerRadiusTopRight=9,
).encode(
    x=alt.X('TU', title='TU'),  # Adicione a transformação sort aqui
    y=alt.Y('Dcr Frente Operação', title='Dcr Frente Operação', sort='-x'),
    tooltip=['Dcr Frente Operação', 'TU']
).properties(
    height=altura_grafico,
    title='Tava de Utilização por Módulo'
).configure_axis(grid=False).configure_view(strokeWidth=0)




col1, col2 = st.columns([1,1])

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.altair_chart(fig4, use_container_width=True)


col1, col2 = st.columns([1,1])

with col1:
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.altair_chart(fig5, use_container_width=True)
    
    
col1, col2 = st.columns([1,1])

with col1:
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.altair_chart(fig6, use_container_width=True)