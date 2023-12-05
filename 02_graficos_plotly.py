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

pip install --upgrade nbformat

df = pd.read_excel("Producao Colheita.xlsx")
            
fig = px.scatter(df, x='VMI (m³)', y='Produtividade', color='Dcr Frente Operação')

fig.show()

