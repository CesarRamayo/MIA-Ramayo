import streamlit as st
import requests
import json
import os

API_URL = "http://localhost:8000"
HISTORIAL_FILE = "data/chat_history.json"

st.set_page_config(page_title="RAG App", page_icon="🤖", layout="wide")
st.title("📚 Sistema RAG - Proyecto Final")

# --- FUNCIONES DE HISTORIAL LOCAL ---
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_historial(mensajes):
    os.makedirs("data", exist_ok=True)
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=4)

# --- INICIALIZAR EL HISTORIAL Y VARIABLES DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = cargar_historial()
    
if "show_error" not in st.session_state:
    st.session_state.show_error = False
if "retry_flag" not in st.session_state:
    st.session_state.retry_flag = False
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

def get_indexed_documents():
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            return response.json().get("documents", [])
    except:
        return []
    return []

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("1. Cargar Documentos")
    st.write("Sube PDFs o textos (.txt, .md). Si subes un archivo que ya existe, se reindexará automáticamente.")
    
    uploaded_file = st.file_uploader("Sube un archivo", type=['txt', 'md', 'pdf'])
    
    if st.button("Indexar Documento"):
        if uploaded_file is not None:
            with st.spinner("Procesando e indexando..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/ingest", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"¡Éxito! Se guardaron {data['chunks_creados']} fragmentos.")
                    st.rerun() 
                else:
                    st.error(f"Error al indexar: {response.text}")
        else:
            st.warning("Por favor sube un archivo primero.")

    st.divider()
    
    st.header("📂 Documentos en Base de Datos")
    docs = get_indexed_documents()
    
    if docs:
        for doc in docs:
            col1, col2 = st.columns([8, 2])
            with col1:
                st.write(f"📄 `{doc}`")
            with col2:
                if st.button("🗑️", key=f"del_{doc}", help=f"Borrar {doc}"):
                    requests.delete(f"{API_URL}/documents/{doc}")
                    st.rerun()
    else:
        st.info("No hay documentos indexados aún.")
        
    st.divider()
    
    st.header("⚙️ Configuración")
    top_k = st.slider("Fragmentos a recuperar (Top-K):", min_value=1, max_value=5, value=3)

    st.header("🔍 Filtro de Búsqueda")
    opciones_filtro = ["Todos los documentos"] + docs
    archivo_seleccionado = st.selectbox("Consultar en:", opciones_filtro)

    if st.button("🗑️ Limpiar historial de chat"):
        st.session_state.messages = []
        st.session_state.show_error = False
        st.session_state.last_prompt = ""
        guardar_historial([]) 
        st.rerun()

# --- ÁREA PRINCIPAL: EL CHAT ---
st.header("2. Consultar Base de Datos")

# 1. Dibujar el historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            with st.expander("Ver Evidencia Recuperada (Citas)"):
                for idx, cit in enumerate(msg["citations"]):
                    st.markdown(f"**[{idx+1}] Fuente:** `{cit['source']}` (Distancia: {cit['score']:.4f})")
                    st.caption(f"_{cit['text']}_")

# 2. Manejo de error visual (Si falló, lo mostramos una vez y lo apagamos)
if st.session_state.show_error:
    st.error("⚠ Fallo en la comunicación con la IA o el servidor está saturado (Error 503).")
    st.session_state.show_error = False

# 3. Botón de regenerar/reintentar SIEMPRE VISIBLE si hay una última pregunta
if st.session_state.last_prompt:
    # Usamos columnas para darle un mejor estilo visual y que no ocupe toda la pantalla
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Regenerar respuesta"):
            # Si la última burbuja fue de la IA, la quitamos del historial para reescribirla
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
                st.session_state.messages.pop()
                guardar_historial(st.session_state.messages)
                
            st.session_state.retry_flag = True
            st.rerun()

prompt = st.chat_input("Haz una pregunta sobre tus documentos...")

if st.session_state.retry_flag:
    prompt = st.session_state.last_prompt
    st.session_state.retry_flag = False

if prompt:
    st.session_state.last_prompt = prompt
    
    # Evitamos duplicar la burbuja del usuario si le dio clic a "Regenerar"
    if not st.session_state.messages or st.session_state.messages[-1]["role"] != "user" or st.session_state.messages[-1]["content"] != prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        guardar_historial(st.session_state.messages) 
        with st.chat_message("user"):
            st.markdown(prompt)
            
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos y generando respuesta..."):
            filtro_real = None if archivo_seleccionado == "Todos los documentos" else archivo_seleccionado
            payload = {"question": prompt, "top_k": top_k, "source_filter": filtro_real}
            
            try:
                response = requests.post(f"{API_URL}/query", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result['answer']
                    citations = result['citations']
                    abstained = result['abstained']
                    
                    if abstained:
                        st.warning("⚠ El sistema no encontró evidencia suficiente y se abstuvo de responder.")
                    
                    st.markdown(answer)
                    
                    if citations:
                        with st.expander("Ver Evidencia Recuperada (Citas)"):
                            for idx, cit in enumerate(citations):
                                st.markdown(f"**[{idx+1}] Fuente:** `{cit['source']}` (Distancia: {cit['score']:.4f})")
                                st.caption(f"_{cit['text']}_")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations
                    })
                    guardar_historial(st.session_state.messages)
                    # Forzamos recarga para que el botón "Regenerar" aparezca limpiamente abajo
                    st.rerun() 
                    
                else:
                    st.session_state.show_error = True
                    st.rerun() 
                    
            except Exception as e:
                st.session_state.show_error = True
                st.rerun()