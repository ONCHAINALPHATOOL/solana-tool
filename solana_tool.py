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
st.title("Gestión de Wallets y Entidades")

# Sección para agregar nuevas entidades y wallets
st.header("Agregar Entidad y Wallet")

# Inputs para agregar una entidad y una wallet
nueva_entidad = st.text_input("Nombre de la Entidad")
nueva_wallet = st.text_input("Dirección de la Wallet")
nuevo_label = st.text_input("Label de la Wallet")

# Botón para agregar una wallet
if st.button("Agregar Wallet"):
    if nueva_entidad and nueva_wallet and nuevo_label:
        if nueva_entidad not in entidades_data:
            entidades_data[nueva_entidad] = []
        entidades_data[nueva_entidad].append({"label": nuevo_label, "direccion": nueva_wallet})
        guardar_datos()
        st.success(f"Wallet agregada a la entidad {nueva_entidad}")
    else:
        st.error("Por favor, completa todos los campos")

# Sección para mostrar las entidades y wallets actuales
st.header("Entidades y Wallets")
for entidad, wallets in entidades_data.items():
    st.subheader(f"Entidad: {entidad}")
    for wallet in wallets:
        st.write(f"Label: {wallet['label']}, Dirección: {wallet['direccion']}")

# Sección para gestionar (editar y eliminar) wallets
st.header("Gestionar Wallets")

# Dropdown para seleccionar una entidad
entidad_seleccionada = st.selectbox("Selecciona una Entidad", list(entidades_data.keys()))

if entidad_seleccionada:
    # Dropdown para seleccionar una wallet dentro de la entidad seleccionada
    wallet_seleccionada = st.selectbox(
        "Selecciona una Wallet",
        [wallet['label'] for wallet in entidades_data[entidad_seleccionada]]
    )

    # Cargar datos de la wallet seleccionada
    if wallet_seleccionada:
        wallet_info = next(
            (wallet for wallet in entidades_data[entidad_seleccionada] if wallet['label'] == wallet_seleccionada), None
        )

        if wallet_info:
            # Mostrar información de la wallet seleccionada
            st.write(f"Dirección: {wallet_info['direccion']}")

            # Inputs para editar la wallet seleccionada
            nuevo_label = st.text_input("Nuevo Label", value=wallet_info['label'])
            nueva_direccion = st.text_input("Nueva Dirección", value=wallet_info['direccion'])

            # Botón para guardar los cambios
            if st.button("Guardar Cambios"):
                wallet_info['label'] = nuevo_label
                wallet_info['direccion'] = nueva_direccion
                guardar_datos()
                st.success(f"Wallet '{nuevo_label}' actualizada correctamente.")

            # Botón para eliminar la wallet
            if st.button("Eliminar Wallet"):
                entidades_data[entidad_seleccionada] = [
                    wallet for wallet in entidades_data[entidad_seleccionada] if wallet['label'] != wallet_seleccionada
                ]
                guardar_datos()
                st.success(f"Wallet '{wallet_seleccionada}' eliminada correctamente.")
