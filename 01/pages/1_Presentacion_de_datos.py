import streamlit as st
import pandas as pd

st.header("Exploración y Dashboard")
df = pd.read_csv("data/inmuebles.csv")

# Filtros básicos
ciudad = st.selectbox("Ciudad", df["ciudad"].unique())
filtrado = df[df["ciudad"] == ciudad]

st.map(filtrado)  # si contiene lat/lon
st.dataframe(filtrado)