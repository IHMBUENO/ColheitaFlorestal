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
    page_title="Produção / Produtividade",
    page_icon="&#xF5E2",
    layout='wide',
    initial_sidebar_state="expanded"
)

### -------------------------------------------------------------------------------
### -------------------------- Importando dados
### -------------------------------------------------------------------------------


def busca_df():
    df = pd.read_excel("fProdutividade.xlsx")
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
    st.subheader("MENU - INDICADORES PRODUTIVIDADE COLHEITA FLORESTAL")
    
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
 
### --------------------------------------------------------------------------------------
### ---------------------------------- Criar Tabelas
### -------------------------------------------------------------------------------------

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

df_filtrado["Mês Núm."] = df_filtrado['Data Operação'].dt.month
df_filtrado["Mês-Ano"] = df_filtrado['Data Operação'].dt.strftime('%m-%Y')


display = st.checkbox('Exibir Dados Diários')

if display:
   st.write(df_filtrado[['Ano',"Mês-Ano",'Mês',"Data Operação",'Fazenda','Projeto','Talhão','Cd Operação', 
            'Dcr Frente Operação', 'Dcr Funcionário Operador', 'Vlr Volume Apontado',
            'Vlr Volume Ajustado', 'Vlr Volume Eficiência', 'Vol. Untário','Produtividade (m³/h)']])


        
cor_grafico = '#aed581'
altura_grafico = 500


## ===============================================================================================
## ----------------------------------------- Gráficos Gerais
## ===============================================================================================

### ------------------------------------------------------------------
## ----------------------- Gráfico de Barras

dados_gerais = df_filtrado.pivot_table(index=['Mês-Ano','Cd Operação'],values='Vlr Volume Ajustado', aggfunc=sum).reset_index()

df_card = df_filtrado.groupby(["Mês-Ano"]).agg({
    'Vlr Volume Ajustado':'sum',
    'Vol. Untário':'mean',
    'Produtividade (m³/h)':'mean'
})
## ===============================================================================================
## ----------------------------------------- Ticket
## ===============================================================================================

V_AJUS = round(df_card['Vlr Volume Ajustado'].mean(),2)
PMEDIA = round(df_card['Produtividade (m³/h)'].mean(),2)
VMI = round(df_card['Vol. Untário'].mean(),2)

st.header(':bar_chart: Indicadores Produção/Produtividade')

dist1,dist2,dist3 = st.columns([1,1,1])

with dist1:
    st.write('**PRODUÇÃO VOL. AJUSTADO MÉDIO:**') ## ** Negrito
    st.info(f"{V_AJUS}(m³/mês)")
    
with dist2:
    st.write('**PRODUTIVIDADE MÉDIA:**')
    st.info(f"{PMEDIA}(m³/h)")
    
with dist3:
     st.write('**VOLUME MÉDIO INDIVIDUAL**')
     st.info(f"{VMI}(m³/ind)")
     
st.markdown("---")


fig1 = px.bar(dados_gerais, x='Mês-Ano', y='Vlr Volume Ajustado', 
             color='Cd Operação', barmode='group', color_discrete_sequence=['#4CAF50', '#8BC34A'])
fig1.update_layout(title='Distribuição Mensal do Volume Total Ajustado por Operação')



## ---------------------- Gráfico de Pizza

fig2 = px.pie(df_filtrado[df_filtrado['Cd Operação'] == 'Corte Harvester'], names='Dcr Frente Operação', values='Vlr Volume Ajustado',
             color_discrete_sequence=px.colors.sequential.Greens)
fig2.update_layout(title='Distribuição de Volume Ajustado<br>por Frente de Operação - Corte Harvester',
                   title_font=dict(size=14),
                  showlegend=False)
fig2.update_traces(textinfo='label+percent', texttemplate='%{label}<br><b>%{percent:.1%}</b>')



fig3 = px.pie(df_filtrado[df_filtrado['Cd Operação'] == 'Baldeio Forwarder'], names='Dcr Frente Operação', values='Vlr Volume Ajustado',
             color_discrete_sequence=px.colors.sequential.Greens)
fig3.update_layout(title='Distribuição de Volume Ajustado<br>por Frente de Operação - Baldeio Forwarder',
                   title_font=dict(size=14),
                  showlegend=False)
fig3.update_traces(textinfo='label+percent', texttemplate='%{label}<br><b>%{percent:.1%}</b>')



col1, col2, col3 = st.columns([2,1,1])

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    st.plotly_chart(fig3, use_container_width=True)
    
 
## ===============================================================================================
## ----------------------------------------- Gráficos de Produtividade
## ===============================================================================================

df_curva = df_filtrado[(df_filtrado['Produtividade (m³/h)'] >10)&(df_filtrado['Produtividade (m³/h)'] <100)&(df_filtrado['Cd Operação']=='Corte Harvester')]
df_curva = df_curva.groupby(['Dcr Frente Operação','Vol. Untário']).agg({
    'Produtividade (m³/h)':'mean'
}).reset_index()

# Função para ajustar uma curva (exemplo: uma função quadrática)
def func(x, a, b, c):
    return a * x**2 + b * x + c

# Ajuste da curva aos dados
popt, _ = curve_fit(func, df_curva['Vol. Untário'], df_curva['Produtividade (m³/h)'])

# Geração de pontos para a curva ajustada
x_fit = np.linspace(df_curva['Vol. Untário'].min(), df_curva['Vol. Untário'].max(), 100)
y_fit = func(x_fit, *popt)

# Criação do gráfico de dispersão
fig4 = px.scatter(df_curva, x='Vol. Untário', y='Produtividade (m³/h)',
                   title="Corte Harvester")

# Adição dos pontos verdes no gráfico
fig4.add_trace(go.Scatter(x=df_curva['Vol. Untário'], y=df_curva['Produtividade (m³/h)'], mode='markers', name='Pontos', marker=dict(color='green')))

# Adição da curva ajustada vermelha no gráfico
fig4.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name='Curva Ajustada', line=dict(color='red')))

# Adição da equação no gráfico
equation = f"Equação da Curva: {popt[0]:.2f}x² + {popt[1]:.2f}x + {popt[2]:.2f}"
fig4.add_annotation(x=0.5, y=0.9, xref="paper", yref="paper",
                    text=equation,
                    showarrow=False,
                    font=dict(size=14, color="white"))


## ===============================================================================================
## ----------------------------------------- Baldeio

df_curva = df_filtrado[(df_filtrado['Produtividade (m³/h)'] >10)&(df_filtrado['Produtividade (m³/h)'] <100)&(df_filtrado['Cd Operação']=='Baldeio Forwarder')]
df_curva = df_curva.groupby(['Dcr Frente Operação','Vol. Untário']).agg({
    'Produtividade (m³/h)':'mean'
}).reset_index()

# Supondo que df_curva tenha as colunas 'Vol. Untário' e 'Produtividade (m³/h)'
df_curva = df_curva.dropna(subset=['Vol. Untário', 'Produtividade (m³/h)'])

# Agora, verifique se há valores nulos nas colunas relevantes
if df_curva['Vol. Untário'].isnull().any() or df_curva['Produtividade (m³/h)'].isnull().any():
    print("Existem valores nulos nas colunas relevantes.")
else:
    print("Não há valores nulos nas colunas relevantes.")

# Função para ajustar uma curva (exemplo: uma função quadrática)
def func(x, a, b, c):
    return a * x**2 + b * x + c

# Ajuste da curva aos dados
popt, _ = curve_fit(func, df_curva['Vol. Untário'], df_curva['Produtividade (m³/h)'])

# Geração de pontos para a curva ajustada
x_fit = np.linspace(df_curva['Vol. Untário'].min(), df_curva['Vol. Untário'].max(), 100)
y_fit = func(x_fit, *popt)

# Criação do gráfico de dispersão
fig5 = px.scatter(df_curva, x='Vol. Untário', y='Produtividade (m³/h)',
                  title="Baldeiro Forwarder")

# Adição dos pontos verdes no gráfico
fig5.add_trace(go.Scatter(x=df_curva['Vol. Untário'], y=df_curva['Produtividade (m³/h)'], mode='markers', name='Pontos', marker=dict(color='green')))

# Adição da curva ajustada vermelha no gráfico
fig5.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name='Curva Ajustada', line=dict(color='red')))

# Adição da equação no gráfico
equation = f"Equação da Curva: {popt[0]:.2f}x² + {popt[1]:.2f}x + {popt[2]:.2f}"
fig5.add_annotation(x=0.5, y=0.9, xref="paper", yref="paper",
                    text=equation,
                    showarrow=False,
                    font=dict(size=14, color="white")
                    )


col1, col2 = st.columns([1,1])

with col1:
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.plotly_chart(fig5, use_container_width=True)


##### =============================================================================
#### ------------ Produtividade por Módulo HV

df_produtiv_modulo_hv = df_filtrado[(df_filtrado['Produtividade (m³/h)'] >10)&(df_filtrado['Produtividade (m³/h)'] <100)&
                                 (df_filtrado['Cd Operação']=='Corte Harvester')]
df_produtiv_modulo_hv = df_produtiv_modulo_hv.groupby(['Dcr Frente Operação']).agg({
    'Produtividade (m³/h)':'mean'
}).reset_index()

Fig5 = px.bar(df_produtiv_modulo_hv, x='Dcr Frente Operação', y='Produtividade (m³/h)', 
             barmode='group', color_discrete_sequence=['green'])

Fig5.update_layout(
    xaxis=dict(categoryorder='total descending')
)

Fig5.update_layout(title='Produtividade Média por Módulo - HV')



##### =============================================================================
#### ------------ Produtividade por Módulo FW

df_produtiv_modulo_fw = df_filtrado[(df_filtrado['Produtividade (m³/h)'] >10)&(df_filtrado['Produtividade (m³/h)'] <100)&
                                 (df_filtrado['Cd Operação']=='Baldeio Forwarder')]
df_produtiv_modulo_fw = df_produtiv_modulo_fw.groupby(['Dcr Frente Operação']).agg({
    'Produtividade (m³/h)':'mean'
}).reset_index()

Fig6 = px.bar(df_produtiv_modulo_fw, x='Dcr Frente Operação', y='Produtividade (m³/h)', 
             barmode='group', color_discrete_sequence=['green'])

Fig6.update_layout(
    xaxis=dict(categoryorder='total descending')
)

Fig6.update_layout(title='Produtividade Média por Módulo - FW')



col1, col2 = st.columns([1,1])

with col1:
    st.plotly_chart(Fig5, use_container_width=True)

with col2:
    st.plotly_chart(Fig6, use_container_width=True)

















# ## ----------------------------------- TABELA PRODUÇÃO BALDEIO

# tabela_mes_prod_baldeio = df[df['Cd Operação'] == "Baldeio Forwarder"].copy()

# if fModulo:
#     tabela_mes_prod_baldeio = tabela_mes_prod_baldeio[tabela_mes_prod_baldeio['Dcr Frente Operação'].isin(fModulo)]

# tabela_mes_prod_baldeio = tabela_mes_prod_baldeio.groupby(["Mês - Ano"]).agg({
#     "Vlr Volume Apontado":"sum",
#     "Vlr Volume Ajustado":"sum",
#     "Vlr Volume Eficiência":"sum",
#     "VMI (m³)":"mean",
#     "Produtividade":"mean"
# }).reset_index()


# ## ----------------------------------- TABELA PRODUTIVIDADE CORTE

# tabela_mes_prod_corte = df[df['Cd Operação'] == "Corte Harvester"].copy()

# if fModulo:
#     tabela_mes_prod_corte = tabela_mes_prod_corte[tabela_mes_prod_corte['Dcr Frente Operação'].isin(fModulo)]

# tabela_mes_prod_corte = tabela_mes_prod_corte.groupby(["Mês - Ano"]).agg({
#     "Vlr Volume Apontado":"sum",
#     "Vlr Volume Ajustado":"sum",
#     "Vlr Volume Eficiência":"sum",
#     "VMI (m³)":"mean",
#     "Produtividade":"mean"
# }).reset_index()


# cor_grafico = '#aed581'
# altura_grafico = 500

# ### ==============================================================================================================
# ### ---------------------------------- Gráficos HV
# ### ==============================================================================================================


# graf2_prod_corte = alt.Chart(tabela_mes_prod_corte).mark_bar(
#     color = cor_grafico,
#     cornerRadiusTopLeft=9,
#     cornerRadiusTopRight=9,
# ).encode(
#     x='Mês - Ano',
#     y='Vlr Volume Apontado',
#     tooltip=['Mês - Ano', 'Vlr Volume Apontado']
# ).properties(height = altura_grafico,
#              title='Volume Total Apontado (m³) - Corte'
# ).configure_axis(grid=False).configure_view(strokeWidth=0)

# st.altair_chart(graf2_prod_corte, use_container_width=True)






# ## ---------------------------------- BALDEIO PRODUÇÃO TOTAL

# cor_grafico = '#aed581'
# altura_grafico = 500

# graf1_prod_baldeio = alt.Chart(tabela_mes_prod_baldeio).mark_bar(
#     color = cor_grafico,
#     cornerRadiusTopLeft=9,
#     cornerRadiusTopRight=9,
# ).encode(
#     x='Mês - Ano',
#     y='Vlr Volume Apontado',
#     tooltip=['Mês - Ano', 'Vlr Volume Apontado']
# ).properties(height = altura_grafico,
#              title='Volume Total Apontado (m³) - Baldeio'
# ).configure_axis(grid=False).configure_view(strokeWidth=0)

# st.altair_chart(graf1_prod_baldeio, use_container_width=True)

# ## ---------------------------------- COLHEITA PRODUÇÃO TOTAL

# graf2_prod_corte = alt.Chart(tabela_mes_prod_corte).mark_bar(
#     color = cor_grafico,
#     cornerRadiusTopLeft=9,
#     cornerRadiusTopRight=9,
# ).encode(
#     x='Mês - Ano',
#     y='Vlr Volume Apontado',
#     tooltip=['Mês - Ano', 'Vlr Volume Apontado']
# ).properties(height = altura_grafico,
#              title='Volume Total Apontado (m³) - Corte'
# ).configure_axis(grid=False).configure_view(strokeWidth=0)

# st.altair_chart(graf2_prod_corte, use_container_width=True)



# df = px.data.iris()
# df.head()
# # Criar o gráfico de dispersão com cores diferenciadas por espécie
# fig = px.scatter(df, x='sepal_length', y='petal_length',
#                  color='species',
#                  title="Plantas",
#                  labels={'sepal_length': 'Comprimento da Sépala',
#                          'petal_length': 'Comprimento da Pétala'},
#                  height=600, width=600)

# # Mostrar o gráfico no Streamlit
# st.plotly_chart(fig, use_container_width=True)
# plotly.__version__