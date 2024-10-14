import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Autenticación con Google Sheets usando los secretos almacenados en Streamlit
def autenticar_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive"]
    
    credentials = Credentials.from_service_account_info(
        st.secrets["GCP_CREDENTIALS"], scopes=scope)
    
    client = gspread.authorize(credentials)
    return client

# Función para obtener los datos desde Google Sheets
def obtener_datos_hoja(sheet_id, sheet_name):
    client = autenticar_google_sheets()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    return data

# Función para agregar una nueva wallet en Google Sheets
def agregar_wallet_google_sheets(sheet_id, sheet_name, entidad, label, direccion):
    client = autenticar_google_sheets()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    sheet.append_row([entidad, label, direccion])

# Tu ID de la hoja de Google Sheets (puedes obtenerlo de la URL de tu hoja de cálculo)
SHEET_ID = "1IixRfnvy9PwuvKsD_40VyaFRhTrRAS7I2CXJbps1AE9"  # Reemplazar con el ID de tu hoja
SHEET_NAME = "MAIN"  # Cambia el nombre de la hoja si es necesario

# Cargar los datos desde Google Sheets al iniciar
datos_wallets = obtener_datos_hoja(SHEET_ID, SHEET_NAME)

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
        agregar_wallet_google_sheets(SHEET_ID, SHEET_NAME, nueva_entidad, nuevo_label, nueva_wallet)
        st.success(f"✅ Wallet agregada a la entidad '{nueva_entidad}'")
    else:
        st.error("❌ Por favor, completa todos los campos")

# Separador visual
st.markdown("---")

# Sección para mostrar entidades y wallets
st.header("Listado de Entidades y Wallets")
for fila in datos_wallets:
    entidad = fila['Entidad']
    label = fila['Label']
    direccion = fila['Dirección']
    st.markdown(f"📌 Entidad: **{entidad}** - 🔹 **Label**: {label}, **Dirección**: `{direccion}`")

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

            # Botón para guardar los cambios (esto requerirá una implementación adicional para modificar en Google Sheets)
            if st.button("Guardar Cambios", key="guardar_cambios"):
                st.error("Esta funcionalidad no está implementada para Google Sheets.")

            # Botón para eliminar la wallet (esto requerirá una implementación adicional para modificar en Google Sheets)
            if st.button("Eliminar Wallet", key="eliminar_wallet"):
                st.error("Esta funcionalidad no está implementada para Google Sheets.")

