import streamlit as st
import dropbox
import json

# Función para autenticarse en Dropbox usando el token de acceso
def conectar_dropbox():
    dbx = dropbox.Dropbox(st.secrets["dropbox"]["ACCESS_TOKEN"])
    return dbx

# Función para cargar un archivo JSON desde Dropbox
def cargar_json_desde_dropbox(ruta_archivo):
    dbx = conectar_dropbox()
    try:
        _, res = dbx.files_download(ruta_archivo)
        datos = json.loads(res.content)
    except dropbox.exceptions.ApiError as e:
        # Si no existe el archivo, devolvemos una lista vacía
        datos = []
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

# Botón para agregar
if st.button("Agregar Wallet"):
    if nueva_entidad and nueva_wallet and nuevo_label:
        # Agregar la nueva wallet a la lista de datos
        nueva_wallet_info = {"Entidad": nueva_entidad, "Label": nuevo_label, "Dirección": nueva_wallet}
        datos_wallets.append(nueva_wallet_info)
        guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
        st.success(f"✅ Wallet agregada a la entidad '{nueva_entidad}'")
    else:
        st.error("❌ Por favor, completa todos los campos")

# Separador visual
st.markdown("---")

# Sección para mostrar entidades y wallets
st.header("Listado de Entidades y Wallets")
if datos_wallets:
    for fila in datos_wallets:
        entidad = fila['Entidad']
        label = fila['Label']
        direccion = fila['Dirección']
        st.markdown(f"📌 Entidad: **{entidad}** - 🔹 **Label**: {label}, **Dirección**: `{direccion}`")
else:
    st.write("No hay wallets registradas.")

# Separador visual
st.markdown("---")

# Sección para buscar una wallet por dirección
st.header("Buscar Wallet por Dirección")
direccion_busqueda = st.text_input("🔎 Introduce la dirección de la wallet")

if st.button("Buscar Wallet"):
    encontrado = False
    for fila in datos_wallets:
        if fila['Dirección'] == direccion_busqueda:
            st.success(f"✅ Dirección encontrada. Entidad: **{fila['Entidad']}**, Label: **{fila['Label']}**")
            encontrado = True
            break
    if not encontrado:
        st.error("❌ No se encontró ninguna wallet con esa dirección.")

# Separador visual
st.markdown("---")

# Sección para gestionar (editar y eliminar) wallets
st.header("Modificar Wallets")

# Dropdown para seleccionar una entidad con clave única
entidad_seleccionada = st.selectbox("Selecciona una Entidad", [fila['Entidad'] for fila in datos_wallets], key="entidad_editar")

if entidad_seleccionada:
    # Dropdown para seleccionar una wallet dentro de la entidad seleccionada, también con clave única
    wallets_filtradas = [fila for fila in datos_wallets if fila['Entidad'] == entidad_seleccionada]
    wallet_seleccionada = st.selectbox(
        "Selecciona una Wallet",
        [fila['Label'] for fila in wallets_filtradas],
        key="wallet_editar"
    )

    # Cargar datos de la wallet seleccionada
    if wallet_seleccionada:
        wallet_info = next(
            (fila for fila in wallets_filtradas if fila['Label'] == wallet_seleccionada), None
        )

        if wallet_info:
            # Mostrar información de la wallet seleccionada
            st.write(f"Dirección: {wallet_info['Dirección']}")

            # Inputs para editar la wallet seleccionada
            nuevo_label = st.text_input("Nuevo Label", value=wallet_info['Label'], key="nuevo_label")
            nueva_direccion = st.text_input("Nueva Dirección", value=wallet_info['Dirección'], key="nueva_direccion")

            # Botón para guardar los cambios
            if st.button("Guardar Cambios", key="guardar_cambios"):
                # Actualizar los datos
                wallet_info['Label'] = nuevo_label
                wallet_info['Dirección'] = nueva_direccion
                guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
                st.success("Cambios guardados exitosamente")

            # Botón para eliminar la wallet
            if st.button("Eliminar Wallet", key="eliminar_wallet"):
                datos_wallets.remove(wallet_info)
                guardar_json_en_dropbox(ARCHIVO_JSON, datos_wallets)
                st.success("Wallet eliminada exitosamente")

