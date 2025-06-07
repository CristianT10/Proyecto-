import streamlit as st
import pandas as pd

st.header("Buscar y comparar inmuebles")

df = pd.read_csv("data/inmuebles.csv")
buscar = st.text_input("Buscar por ID, dirección o barrio")

if buscar:
    resultado = df[df["id"].astype(str).str.contains(buscar) |
                   df["direccion"].str.contains(buscar, case=False) |
                   df["barrio"].str.contains(buscar, case=False)]
    st.dataframe(resultado)

    if len(resultado) >= 2:
        st.subheader("Comparación")
        st.bar_chart(resultado[["precio", "superficie"]].set_index(resultado["id"]))
