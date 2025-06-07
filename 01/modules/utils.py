# utils.py
# utils.py
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def load_data(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def format_currency(value) -> str:
    try:
        return f"{value:,.0f} €".replace(",", ".")
    except:
        return "-"

def load_secret(key: str) -> str:
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, "")
def mostrar_tarjetas(df):
    for idx, row in df.iterrows():
        with st.container():
            cols = st.columns([1, 2])
            with cols[0]:
                st.image("https://via.placeholder.com/150", width=150)  # Reemplaza con la URL de la imagen del vehículo si está disponible
            with cols[1]:
                st.subheader(f"{row['Marca']} {row['Modelo']}")
                st.write(f"💰 Precio: {format_currency(row['Precio'])}")
                st.write(f"📍 Ubicación: {row['Ubicación']}")
                st.write(f"🛣️ Kilometraje: {row['Kilometraje']} km")
                st.write(f"🛢️ Combustible: {row['Combustible']}")
                st.write(f"📅 Año: {row['Año de matriculación']}")
                st.write(f"🚗 Tipo: {row['Tipo carrocería']}")
                st.write(f"⚙️ Transmisión: {row['Transmisión']}")
                st.write(f"🔒 Garantía: {row['Garantía']}")
            st.markdown("---")