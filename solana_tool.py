import boto3
import json
import streamlit as st
from io import BytesIO

# Función para conectarse a S3 usando las claves almacenadas en Streamlit Secrets
def conectar_s3():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["default"]["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["default"]["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1"  # Ajusta la región si es diferente
    )
    return s3

# Función para cargar el archivo JSON desde S3
def cargar_json_desde_s3(bucket_name, archivo_json):
    s3 = conectar_s3()
    try:
        # Intentar descargar el archivo JSON
        response = s3.get_object(Bucket=bucket_name, Key=archivo_json)
        contenido_json = response["Body"].read().decode("utf-8")
        datos = json.loads(contenido_json)
        st.success(f"Archivo '{archivo_json}' cargado correctamente.")
        return datos
    except s3.exceptions.NoSuchKey:
        # Si el archivo no existe, retornamos None para inicializar un archivo vacío más tarde
        st.warning(f"El archivo '{archivo_json}' no existe en S3. Se creará uno vacío.")
        return None
    except Exception as e:
        st.error(f"Error al cargar el archivo desde S3: {e}")
        return None

# Función para guardar un archivo JSON en S3
def guardar_json_en_s3(bucket_name, archivo_json, datos):
    s3 = conectar_s3()
    try:
        contenido_json = json.dumps(datos).encode("utf-8")
        s3.put_object(Bucket=bucket_name, Key=archivo_json, Body=contenido_json)
        st.success(f"Archivo '{archivo_json}' guardado correctamente en S3.")
    except Exception as e:
        st.error(f"Error al guardar el archivo en S3: {e}")

# Nombre del bucket y archivo JSON
BUCKET_NAME = "miapp-solana-bucket"
ARCHIVO_JSON = "wallets_data.json"

# Cargar los datos desde S3 al iniciar la app
datos_wallets = cargar_json_desde_s3(BUCKET_NAME, ARCHIVO_JSON)

# Si el archivo no existe o no se encontraron datos, inicializamos con un JSON vacío y lo guardamos
if datos_wallets is None:
    st.warning("No se encontraron datos. Se inicializará un archivo JSON vacío.")
    datos_wallets = {}
    guardar_json_en_s3(BUCKET_NAME, ARCHIVO_JSON, datos_wallets)  # Guardar archivo vacío en S3

# Mostrar los datos en la app (puedes agregar aquí tu lógica de la app)
st.write("Datos cargados:", datos_wallets)

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

# Al cargar la base de datos, mostramos solo un mensaje de éxito.
st.success("Base de datos cargada con éxito.")  # Mensaje de éxito sin mostrar los datos crudos.

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
            
            # Guardar los datos actualizados en S3
            guardar_json_en_s3(BUCKET_NAME, ARCHIVO_JSON, datos_wallets)
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

