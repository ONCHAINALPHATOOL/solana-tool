import streamlit as st
import dropbox
import json
import os

# Función para autenticar con Dropbox usando el token almacenado en los secretos
def conectar_dropbox():
    dbx = dropbox.Dropbox(st.secrets["dropbox"]["ACCESS_TOKEN"])
    return dbx

# Función para cargar un archivo JSON desde Dropbox (si existe)
def cargar_json_desde_dropbox(ruta_archivo):
    dbx = conectar_dropbox()
    try:
        _, res = dbx.files_download(ruta_archivo)
        datos = json.loads(res.content)
    except dropbox.exceptions.ApiError as e:
        # Si no existe el archivo, se inicializan los datos
        st.warning("No se encontró el archivo en Dropbox. Inicializando datos por defecto.")
        datos = {
            "Drae": [{"label": "120K", "direccion": "6N9CDZ7sNRYQ7BWDJX3iLbL3359rVXN9yvwaEebQqEo8d"}],
            "Pedro": [{"label": "christ?", "direccion": "DhxbZcn8oCgafGHSg1WX1bMhv5txGRraVMmR6G6RVnck"}]
        }
    return datos

# Función para guardar un archivo JSON en Dropbox
def guardar_json_en_dropbox(ruta_archivo, datos):
    dbx = conectar_dropbox()
    contenido_json = json.dumps(datos).encode('utf-8')
    dbx.files_upload(contenido_json, ruta_archivo, mode=dropbox.files.WriteMode("overwrite"))

# Ruta del archivo JSON en Dropbox
ARCHIVO_JSON = "/wallets_data.json"

# Cargar los datos desde Dropbox al iniciar
datos_wallets = cargar_json_desde_dropbox(ARCHIVO_JSON)

# Encabezado principal de la aplicación
st.title("SOLANA TOOL ONCHAIN ALPHA")

# Sección para agregar una nueva entidad y wallet
st.header("Agregar Entidad y Wallet")
nueva_entidad = st.text_input("📝 Nombre de la Entidad")
nueva_wallet = st.text_input("🔑 Dirección de la Wallet")
nuevo_label = st.text_input("🏷️ Label de la Wallet")

# Botón para agregar una nueva wallet
if st.button("Agregar Wallet"):
    if nueva_entidad and nueva_wallet and nuevo_label:
        if nueva_entidad in datos_wallets:
            datos_wallets[nueva_entidad].append({"label": nuevo_label, "direccion": nueva_wallet})
        else:
            datos_wallets[nueva_entidad] = [{"label": nuevo_label, "direccion": nueva_wallet}]
        
        # Guardar los datos actualizados en Dropbox
        guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
        st.success(f"✅ Wallet agregada a la entidad '{nueva_entidad}'")
    else:
        st.error("❌ Por favor, completa todos los campos")

# Separador visual
st.markdown("---")

# Sección para mostrar entidades y wallets
st.header("Listado de Entidades y Wallets")
for entidad, wallets in datos_wallets.items():
    st.markdown(f"📌 **{entidad}**")
    for wallet in wallets:
        st.markdown(f"🔹 **Label**: {wallet['label']}, **Dirección**: `{wallet['direccion']}`")

# Separador visual
st.markdown("---")

# Sección para buscar una wallet por dirección
st.header("Buscar Wallet por Dirección")
direccion_busqueda = st.text_input("🔎 Introduce la dirección de la wallet")

if st.button("Buscar Wallet"):
    encontrado = False
    for entidad, wallets in datos_wallets.items():
        for wallet in wallets:
            if wallet['direccion'] == direccion_busqueda:
                st.success(f"✅ Dirección encontrada. Entidad: **{entidad}**, Label: **{wallet['label']}**")
                encontrado = True
                break
        if encontrado:
            break
    if not encontrado:
        st.error("❌ No se encontró ninguna wallet con esa dirección.")

# Separador visual
st.markdown("---")

# Sección para gestionar (editar y eliminar) wallets
st.header("Modificar Wallets")

# Dropdown para seleccionar una entidad con clave única
entidad_seleccionada = st.selectbox("Selecciona una Entidad", list(datos_wallets.keys()), key="entidad_editar")

if entidad_seleccionada:
    # Dropdown para seleccionar una wallet dentro de la entidad seleccionada, también con clave única
    wallets_filtradas = datos_wallets[entidad_seleccionada]
    wallet_seleccionada = st.selectbox(
        "Selecciona una Wallet",
        [wallet['label'] for wallet in wallets_filtradas],
        key="wallet_editar"
    )

    # Cargar datos de la wallet seleccionada
    if wallet_seleccionada:
        wallet_info = next(
            (wallet for wallet in wallets_filtradas if wallet['label'] == wallet_seleccionada), None
        )

        if wallet_info:
            # Mostrar información de la wallet seleccionada
            st.write(f"Dirección: {wallet_info['direccion']}")

            # Inputs para editar la wallet seleccionada
            nuevo_label = st.text_input("Nuevo Label", value=wallet_info['label'], key="nuevo_label")
            nueva_direccion = st.text_input("Nueva Dirección", value=wallet_info['direccion'], key="nueva_direccion")

            # Botón para guardar los cambios (esto requerirá una implementación adicional para modificar en Google Sheets)
            if st.button("Guardar Cambios", key="guardar_cambios"):
                wallet_info['label'] = nuevo_label
                wallet_info['direccion'] = nueva_direccion
                guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
                st.success("✅ Cambios guardados correctamente.")

            # Botón para eliminar la wallet
            if st.button("Eliminar Wallet", key="eliminar_wallet"):
                datos_wallets[entidad_seleccionada].remove(wallet_info)
                guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
                st.success("✅ Wallet eliminada correctamente.")
