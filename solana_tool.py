import streamlit as st
import json
import os

# Ruta del archivo JSON donde se guardarán los datos
ruta_archivo = 'wallets_data.json'

# Función para guardar los datos en un archivo JSON
def guardar_datos():
    with open(ruta_archivo, 'w') as f:
        json.dump(entidades_data, f)

# Función para cargar los datos desde un archivo JSON (si existe)
def cargar_datos():
    global entidades_data
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, 'r') as f:
            entidades_data = json.load(f)
    else:
        # Si no existe el archivo, se inicializan los datos
        entidades_data = {
            "Drae": [{"label": "120K", "direccion": "6N9CDZ7sNRYQ7BWDJX3iLbL3359rVXN9yvwaEebQqEo8d"}],
            "Pedro": [{"label": "christ?", "direccion": "DhxbZcn8oCgafGHSg1WX1bMhv5txGRraVMmR6G6RVnck"}]
        }

# Cargar los datos al inicio
cargar_datos()

# Encabezado principal de la aplicación
st.title("**SOLANA TOOL ONCHAIN ALPHA**")

# Sección para agregar una nueva entidad y wallet
st.header("Agregar Entidad y Wallet")
nueva_entidad = st.text_input("📝 Nombre de la Entidad")
nueva_wallet = st.text_input("🔑 Dirección de la Wallet")
nuevo_label = st.text_input("🏷️ Label de la Wallet")

# Botón para agregar
if st.button("Agregar Wallet"):
    if nueva_entidad and nueva_wallet and nuevo_label:
        if nueva_entidad not in entidades_data:
            entidades_data[nueva_entidad] = []
        # Validar que no exista el mismo label en la entidad
        if any(wallet['label'] == nuevo_label for wallet in entidades_data[nueva_entidad]):
            st.error(f"❌ El label '{nuevo_label}' ya existe en la entidad '{nueva_entidad}'")
        else:
            entidades_data[nueva_entidad].append({"label": nuevo_label, "direccion": nueva_wallet})
            guardar_datos()
            st.success(f"✅ Wallet agregada a la entidad '{nueva_entidad}'")
    else:
        st.error("❌ Por favor, completa todos los campos")

# Separador visual
st.markdown("---")

# Sección para mostrar entidades y wallets
st.header("📋 **Listado de Entidades y Wallets**")
for entidad, wallets in entidades_data.items():
    st.subheader(f"📌 Entidad: **{entidad}**")
    for wallet in wallets:
        st.markdown(f"🔹 **Label**: {wallet['label']} - **Dirección**: `{wallet['direccion']}`")

# Separador visual
st.markdown("---")

# Sección para gestionar (editar y eliminar) wallets
st.header("🔧 **Modificar Wallets**")

# Dropdown para seleccionar una entidad con clave única
entidad_seleccionada = st.selectbox("Selecciona una Entidad", list(entidades_data.keys()), key="entidad_editar")

if entidad_seleccionada:
    # Dropdown para seleccionar una wallet dentro de la entidad seleccionada
    wallet_seleccionada = st.selectbox(
        "Selecciona una Wallet",
        [wallet['label'] for wallet in entidades_data[entidad_seleccionada]],
        key="wallet_editar"
    )

    # Cargar datos de la wallet seleccionada
    if wallet_seleccionada:
        wallet_info = next(
            (wallet for wallet in entidades_data[entidad_seleccionada] if wallet['label'] == wallet_seleccionada), None
        )

        if wallet_info:
            # Mostrar información de la wallet seleccionada en columnas
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("🏷️ Nuevo Label", value=wallet_info['label'], key="nuevo_label")
            with col2:
                st.text_input("🔑 Nueva Dirección", value=wallet_info['direccion'], key="nueva_direccion")

            # Botón para guardar los cambios
            if st.button("Guardar Cambios", key="guardar_cambios"):
                wallet_info['label'] = st.session_state.nuevo_label
                wallet_info['direccion'] = st.session_state.nueva_direccion
                guardar_datos()
                st.success(f"✅ Wallet '{st.session_state.nuevo_label}' actualizada correctamente.")

            # Botón para eliminar la wallet
            if st.button("Eliminar Wallet", key="eliminar_wallet"):
                entidades_data[entidad_seleccionada] = [
                    wallet for wallet in entidades_data[entidad_seleccionada] if wallet['label'] != wallet_seleccionada
                ]
                guardar_datos()
                st.success(f"🗑️ Wallet '{wallet_seleccionada}' eliminada correctamente.")
