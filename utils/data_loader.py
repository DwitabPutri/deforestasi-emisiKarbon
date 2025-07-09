import pandas as pd
import streamlit as st

@st.cache_data
def load_excel_data(sheet_name):
    return pd.read_excel("data/global_05212025.xlsx", sheet_name=sheet_name)