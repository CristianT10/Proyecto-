# app.py

import streamlit as st
import pandas as pd
import io
from utils import load_data, format_currency, mostrar_tarjetas
from filters import aplicar_todos_los_filtros

st.set_page_config(page_title="Catálogo de Vehículos", layout="wide")
st.title("🚗 Catálogo de Vehículos")

# Cargar datos
df = load_data("data/vehiculos.csv")

if not df.empty:
    # ---------------------- SIDEBAR - FILTROS ----------------------
    st.sidebar.header("🔍 Filtros")

    min_precio = int(df["Precio"].min())
    max_precio = int(df["Precio"].max())
    min_year = int(df["Año de matriculación"].min())
    max_year = int(df["Año de matriculación"].max())

    marcas = sorted(df["Marca"].dropna().unique())
    combustibles = sorted(df["Combustible"].dropna().unique())
    carrocerias = sorted(df["Tipo carrocería"].dropna().unique())

    filtros = {
        "min_precio": st.sidebar.slider("Precio mínimo (€)", min_precio, max_precio, min_precio),
        "max_precio": st.sidebar.slider("Precio máximo (€)", min_precio, max_precio, max_precio),
        "marcas": st.sidebar.multiselect("Marca", marcas, default=marcas),
        "combustibles": st.sidebar.multiselect("Combustible", combustibles, default=combustibles),
        "carrocerias": st.sidebar.multiselect("Tipo de carrocería", carrocerias, default=carrocerias),
        "incluir_km0": st.sidebar.checkbox("Incluir vehículos KM 0", value=True),
        "incluir_demo": st.sidebar.checkbox("Incluir vehículos demo", value=True),
        "min_year": st.sidebar.slider("Año de matriculación (mínimo)", min_year, max_year, min_year),
        "max_year": st.sidebar.slider("Año de matriculación (máximo)", min_year, max_year, max_year)
    }

    # ---------------------- FILTRAR DATA ----------------------
    df_filtrado = aplicar_todos_los_filtros(df, filtros)

    # ---------------------- BUSQUEDA ----------------------
    busqueda = st.text_input("🔎 Buscar por modelo o marca:")
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado["Modelo"].str.contains(busqueda, case=False, na=False) |
            df_filtrado["Marca"].str.contains(busqueda, case=False, na=False)
        ]

    # ---------------------- COMPARACIÓN ----------------------
    modelos_para_comparar = st.multiselect(
        "Selecciona vehículos para comparar:",
        options=df_filtrado["Modelo"].unique()
    )

    if modelos_para_comparar:
        df_comparacion = df_filtrado[df_filtrado["Modelo"].isin(modelos_para_comparar)]
        st.subheader("🔎 Comparación de Vehículos Seleccionados")
        st.dataframe(df_comparacion.set_index("Modelo")[[
            "Marca", "Precio", "Kilometraje", "Año de matriculación",
            "Combustible", "Tipo carrocería", "Transmisión", "Garantía"
        ]].style.format({"Precio": format_currency}))

    # ---------------------- PAGINACIÓN ----------------------
    st.markdown("---")
    st.subheader(f"🚘 {len(df_filtrado)} vehículos encontrados")

    items_por_pagina = 10
    total_items = len(df_filtrado)
    total_paginas = (total_items - 1) // items_por_pagina + 1
    pagina_actual = st.number_input("Página", min_value=1, max_value=total_paginas, value=1, step=1)

    inicio = (pagina_actual - 1) * items_por_pagina
    fin = inicio + items_por_pagina
    df_pagina = df_filtrado.iloc[inicio:fin]

    mostrar_tarjetas(df_pagina)

    # ---------------------- EXPORTACIÓN ----------------------
    st.sidebar.markdown("### 📥 Descargar Datos Filtrados")

    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='vehiculos_filtrados.csv',
        mime='text/csv'
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Vehículos')
        writer.save()
        st.sidebar.download_button(
            label="Descargar Excel",
            data=excel_buffer,
            file_name='vehiculos_filtrados.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

else:
    st.warning("No se pudieron cargar los datos.")

