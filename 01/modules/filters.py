# filters.py
import pandas as pd
# filters.py
import pandas as pd

def filtrar_por_precio(df: pd.DataFrame, min_precio: int, max_precio: int) -> pd.DataFrame:
    return df[(df["Precio"] >= min_precio) & (df["Precio"] <= max_precio)]

def filtrar_por_marca(df: pd.DataFrame, marcas: list) -> pd.DataFrame:
    return df[df["Marca"].isin(marcas)]

def filtrar_por_combustible(df: pd.DataFrame, tipos: list) -> pd.DataFrame:
    return df[df["Combustible"].isin(tipos)]

def filtrar_por_km0(df: pd.DataFrame, incluir_km0: bool) -> pd.DataFrame:
    if incluir_km0:
        return df
    return df[df["KM 0"] != "SI"]

def filtrar_por_demo(df: pd.DataFrame, incluir_demo: bool) -> pd.DataFrame:
    if incluir_demo:
        return df
    return df[df["Demo"] != "SI"]

def filtrar_por_anyo_matriculacion(df: pd.DataFrame, min_year: int, max_year: int) -> pd.DataFrame:
    return df[(df["Año de matriculación"] >= min_year) & (df["Año de matriculación"] <= max_year)]

def filtrar_por_tipo_carroceria(df: pd.DataFrame, tipos: list) -> pd.DataFrame:
    return df[df["Tipo carrocería"].isin(tipos)]

def aplicar_todos_los_filtros(df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    df = filtrar_por_precio(df, filtros["min_precio"],_]()

