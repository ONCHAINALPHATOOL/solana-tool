from b2sdk.v1 import InMemoryAccountInfo, B2Api, DownloadDestBytes
import json
import streamlit as st

# Función para autenticar con Backblaze usando los secretos de Streamlit
def conectar_backblaze():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account(
        "production",
        st.secrets["backblaze"]["KEY_ID"],
        st.secrets["backblaze"]["APPLICATION_KEY"]
    )
    return b2_api

# Función para cargar un archivo JSON desde Backblaze
def cargar_json_desde_backblaze(ruta_archivo):
    b2_api = conectar_backblaze()
    bucket = b2_api.get_bucket_by_name(st.secrets["backblaze"]["BUCKET_NAME"])

    try:
        # Crear un objeto de destino en memoria
        destino = DownloadDestBytes()
        
        # Descargar el archivo y pasar el destino explícitamente
        bucket.download_file_by_name(ruta_archivo, destino)

        # Leer el contenido descargado y decodificarlo
        contenido_json = destino.get_bytes()
        datos = json.loads(contenido_json.decode('utf-8'))
        st.success(f"Archivo '{ruta_archivo}' cargado correctamente desde Backblaze.")
        return datos

    except Exception as e:
        st.error(f"Error al cargar el archivo desde Backblaze: {e}")
        return None

# Función para guardar un archivo JSON en Backblaze
def guardar_json_en_backblaze(ruta_archivo, datos):
    try:
        b2_api = conectar_backblaze()
        bucket = b2_api.get_bucket_by_name(st.secrets["backblaze"]["BUCKET_NAME"])
        contenido_json = json.dumps(datos).encode('utf-8')
        bucket.upload_bytes(contenido_json, ruta_archivo)
        st.success(f"Archivo '{ruta_archivo}' guardado/actualizado en Backblaze.")
    except Exception as e:
        st.error(f"Error al guardar el archivo en Backblaze: {e}")

# Ruta del archivo JSON en Backblaze
ARCHIVO_JSON = "wallets_data.json"

# Cargar los datos desde Backblaze al iniciar
datos_wallets = cargar_json_desde_backblaze(ARCHIVO_JSON)

if datos_wallets is None:
    st.error("No se cargaron los datos desde Backblaze.")
else:
    # Aquí puedes agregar el código para manejar los datos cargados correctamente
    st.write("Datos cargados correctamente:", datos_wallets)

# Añadir CSS personalizado para los botones y secciones
st.markdown("""
    <style>
    .option {
        display: inline-block;
        border-radius: 12px;
        background-color: #008CBA;
        color: white;
        text-align: center;
        padding: 15px 32px;
        text-decoration: none;
        font-size: 16px;
        margin: 10px 2px;
        cursor: pointer;
        transition-duration: 0.4s;
    }
    
    .option:hover {
        background-color: #4CAF50;
        color: white;
    }

    .section {
        background-color: #f0f0f0;
        padding: 2px;
        border-radius: 2px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal de la aplicación
st.title("SOLANA TOOL ONCHAIN ALPHA")

# Radiobuttons para seleccionar la opción
opcion = st.radio("👇 Selecciona pestaña", ("🛠️ Agregar/Búsqueda/Modificar Wallets", "📚 Listado de Entidades"))

if opcion == "🛠️ Agregar/Búsqueda/Modificar Wallets":
    
    # Sección para agregar una nueva entidad y wallet
    st.markdown('<div class="section">', unsafe_allow_html=True)  # Inicia la sección
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
            
            # Guardar los datos actualizados en Backblaze
            guardar_json_en_backblaze(ARCHIVO_JSON, datos_wallets)
            st.success(f"✅ Wallet agregada a la entidad '{nueva_entidad}'")
        else:
            st.error("❌ Por favor, completa todos los campos")
    st.markdown('</div>', unsafe_allow_html=True)  # Termina la sección

    # Sección para buscar una wallet por dirección
    st.markdown('<div class="section">', unsafe_allow_html=True)  # Inicia la sección
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
    st.markdown('</div>', unsafe_allow_html=True)  # Termina la sección

elif opcion == "📚 Listado de Entidades":
    # Sección para mostrar entidades y wallets
    st.header("Listado de Entidades y Wallets")
    for entidad, wallets in datos_wallets.items():
        with st.expander(f"📌 {entidad}"):
            for wallet in wallets:
                st.markdown(f"🔹 **Label**: {wallet['label']}, **Dirección**: `{wallet['direccion']}`")
                
                # Enlace para ver las transacciones en SolanaTracker
                url_solanatracker = f"https://www.solanatracker.io/wallet/{wallet['direccion']}"
                
                if st.button(f"Transacciones de {wallet['label']}"):
                    st.markdown(f'<a href="{url_solanatracker}" target="_blank">Abrir en SolanaTracker</a>', unsafe_allow_html=True)
