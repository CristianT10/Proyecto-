import streamlit as st
import pickle
import pandas as pd
import numpy as np
from tensorflow import keras

# Configuración
st.set_page_config(page_title="Predictor de Precios", layout="wide")
st.title("🔧 Predictor de Precios de Vehículos (ML + DL)")

# Cargar y limpiar dataframe
try:
    df_2 = pd.read_csv('C:\\Users\\abner\\proyecto\\Proyecto-\\DB\\datos_limpios.csv')   
    df_2 = df_2.dropna(subset=['combustible', 'tipo_carroceria', 'transmision'])
    
    # Obtener opciones para los selectboxes
    df_d = df_2['modelo'].unique().tolist()
    df_g = df_2['combustible'].unique().tolist()
    df_c = df_2['tipo_carroceria'].unique().tolist()
    df_t = df_2['transmision'].unique().tolist()
    
except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.stop()

# Cargar modelos
@st.cache_resource
def load_models():
    try:
        # Cargar modelo de ML
        with open('C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\mejor_modelo_top.pkl', 'rb') as f:
            ml_model = pickle.load(f)
            
        # Cargar modelo de DL (Keras)
        dl_model = keras.models.load_model('C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\modelo_red_neuronal_mae.keras')  # Ajusta la ruta
        
        # Cargar encoders y scaler
        with open("C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\ohe_combustible.pkl", "rb") as f:
            ohe_combustible = pickle.load(f)
        
        with open("C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\target_encoding_modelo.pkl", "rb") as f:
            target_encoding_modelo = pickle.load(f)
            
        with open("C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\ohe_tipo_carroceria.pkl", "rb") as f:
            ohe_tipo_carroceria = pickle.load(f)    
            
        with open("C:\\Users\\abner\\proyecto\\Proyecto-\\streamlit\\standard_scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
            
        return ml_model, dl_model, ohe_combustible, target_encoding_modelo, ohe_tipo_carroceria, scaler
        
    except Exception as e:
        st.error(f"Error al cargar los modelos: {str(e)}")
        return None, None, None, None, None, None

ml_model, dl_model, ohe_combustible, target_encoding_modelo, ohe_tipo_carroceria, scaler = load_models()

if ml_model is not None and dl_model is not None:
    # Mostrar especificaciones del modelo
    st.sidebar.subheader("Especificaciones del Modelo")
    st.sidebar.write("""
    **Modelos disponibles:**
    1. Machine Learning (Random Forest)
    2. Deep Learning (Red Neuronal)
    
    **Features requeridos:**
    - Modelo
    - Kilometraje
    - Potencia (CV)
    - Año de matriculación
    - Combustible
    - Tipo de carrocería
    - Transmisión
    - Financiación disponible
    """)

    # Formulario de entrada
    with st.form("vehicle_form"):
        st.header("Ingrese los detalles del vehículo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            modelo = st.selectbox("Modelo del Vehículo", options=df_d)
            kilometraje = st.number_input("Kilometraje (km)", min_value=0, value=50000, 
                                         help="Ingrese el kilometraje total del vehículo")
            potencia_cv = st.number_input("Potencia (CV)", min_value=50, max_value=2000, value=120,
                                        help="Caballos de fuerza del motor")
            año_matriculacion = st.slider("Año de matriculación", 2000, 2025, 2020,
                                        help="Año en que el vehículo fue matriculado por primera vez")
            
        with col2:
            combustible = st.selectbox("Tipo de combustible", options=df_g,
                                     help="Seleccione el tipo de combustible que usa el vehículo")
            tipo_carroceria = st.selectbox("Tipo de carrocería", options=df_c,
                                         help="Estilo de carrocería del vehículo")
            transmision = st.radio("Tipo de transmisión", options=df_t, index=0,
                                  help="Sistema de transmisión del vehículo")    
            financiacion_disponible = st.checkbox("Financiación disponible",
                                                help="¿El vehículo tiene opciones de financiación?")
        
        submitted = st.form_submit_button("Predecir Precio")
        
    if submitted:
        try:
            # Crear dataframe con los inputs del usuario
            input_usuario = pd.DataFrame({
                'modelo': [modelo],
                'kilometraje': [kilometraje],
                'potencia_cv': [potencia_cv],
                'año_matriculacion': [año_matriculacion],
                'combustible': [combustible],
                'tipo_carroceria': [tipo_carroceria],
                'transmision': [transmision],
                'financiacion_disponible': [financiacion_disponible]
            })

            # Aplicar transformaciones
            # 1. Target encoding para modelo
            input_usuario['modelo_te'] = input_usuario['modelo'].map(target_encoding_modelo)
            
            # 2. One-hot encoding para combustible
            combustible_encoded = ohe_combustible.transform(input_usuario[['combustible']])
            combustible_cols = [f"combustible_{cat}" for cat in ohe_combustible.categories_[0]]
            df_combustible = pd.DataFrame(combustible_encoded, columns=combustible_cols, index=input_usuario.index)
            input_usuario = pd.concat([input_usuario, df_combustible], axis=1)
            input_usuario.drop(columns=['combustible'], inplace=True)
            
            # 3. One-hot encoding para tipo de carrocería
            tipo_carroceria_encoded = ohe_tipo_carroceria.transform(input_usuario[['tipo_carroceria']])
            tipo_carroceria_cols = [f"tipo_carroceria_{cat}" for cat in ohe_tipo_carroceria.categories_[0]]
            df_tipo_carroceria = pd.DataFrame(tipo_carroceria_encoded, columns=tipo_carroceria_cols, index=input_usuario.index)
            input_usuario = pd.concat([input_usuario, df_tipo_carroceria], axis=1)
            input_usuario.drop(columns=['tipo_carroceria'], inplace=True)
            
            # 4. Convertir transmision 0 manual y 1 automática
            input_usuario['transmision_bin'] = input_usuario['transmision'].apply(lambda x: 1 if x == 'Automática' else 0)  
            input_usuario['transmision_bin'] = input_usuario['transmision_bin'].astype(int)
            
            # 5. Convertir financiación a 0 o 1
            input_usuario['financiacion_disponible'] = input_usuario['financiacion_disponible'].astype(int)
            
            # Definir el orden exacto de columnas requerido por los modelos
            column_order = [
                'modelo_te', 'kilometraje', 'potencia_cv', 'año_matriculacion',
                'combustible_Diésel', 'tipo_carroceria_Deportivo', 'transmision_bin',
                'combustible_Eléctrico', 'financiacion_disponible',
                'combustible_Híbrido Enchufable'
            ]
            
            # Asegurarse de que todas las columnas requeridas existan
            for col in column_order:
                if col not in input_usuario.columns:
                    input_usuario[col] = 0  # Rellenar con 0 si falta alguna columna
            
            # Reordenar columnas exactamente como los modelos esperan
            input_usuario = input_usuario[column_order]
            
            # Escalar los datos
            input_data = scaler.transform(input_usuario)

            # Hacer predicciones con ambos modelos
            precio_ml = ml_model.predict(input_data)[0]
            precio_dl = dl_model.predict(input_data)[0][0]  # Red neuronal devuelve array 2D
            
            # Mostrar resultados en dos columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"## 🖥️ ML (Random Forest)")
                st.success(f"### Precio estimado: €{precio_ml:,.2f}")
                
            with col2:
                st.info(f"## 🧠 DL (Red Neuronal)")
                st.info(f"### Precio estimado: €{precio_dl:,.2f}")
            
            # Mostrar diferencia entre predicciones
            diferencia = abs(precio_ml - precio_dl)
            st.warning(f"**Diferencia entre modelos:** €{diferencia:,.2f} ({diferencia/min(precio_ml, precio_dl)*100:.1f}%)")
            
            # Mostrar detalles técnicos
            with st.expander("📊 Detalles técnicos de la predicción"):
                st.write("**Valores ingresados (transformados):**")
                
                # Crear tabla con los valores transformados
                features_show = [
                    ('Modelo (codificado)', 'modelo_te'),
                    ('Kilometraje', 'kilometraje'),
                    ('Potencia (CV)', 'potencia_cv'),
                    ('Año matriculación', 'año_matriculacion'),
                    ('Combustible Diésel', 'combustible_Diésel'),
                    ('Tipo carrocería Deportivo', 'tipo_carroceria_Deportivo'),
                    ('Transmisión Automática', 'transmision_bin'),
                    ('Combustible Eléctrico', 'combustible_Eléctrico'),
                    ('Financiación disponible', 'financiacion_disponible'),
                    ('Combustible Híbrido Enchufable', 'combustible_Híbrido Enchufable')
                ]
                
                st.table(pd.DataFrame({
                    'Característica': [x[0] for x in features_show],
                    'Valor': [input_usuario[x[1]].values[0] for x in features_show]
                }))
                
                # Mostrar importancia de features si está disponible (solo para ML)
                if hasattr(ml_model, 'feature_importances_'):
                    st.write("**Importancia de características (Random Forest):**")
                    importance_df = pd.DataFrame({
                        'Característica': [x[0] for x in features_show],
                        'Importancia': ml_model.feature_importances_
                    }).sort_values('Importancia', ascending=False)
                    
                    # Mostrar gráfico de importancia de características
                    st.bar_chart(importance_df.set_index('Característica'))
                    
                    # Mostrar tabla con valores numéricos
                    st.write("Valores de importancia:")
                    st.dataframe(importance_df)
            
        except Exception as e:
            st.error(f"Error en la predicción: {str(e)}")
else:
    st.warning("Los modelos no están disponibles. Por favor asegúrate de tener los archivos necesarios en el directorio correcto.")

# Instrucciones para el usuario
st.sidebar.markdown("""
### 📝 Instrucciones:
1. Complete todos los campos del formulario
2. Haga clic en **"Predecir Precio"**
3. Compare los resultados de ambos modelos

### ℹ️ Información adicional:
- **ML (Random Forest):** Modelo basado en árboles de decisión
- **DL (Red Neuronal):** Modelo de aprendizaje profundo
- Los precios son estimaciones basadas en datos históricos
- Consulte la sección de detalles técnicos para más información
""")