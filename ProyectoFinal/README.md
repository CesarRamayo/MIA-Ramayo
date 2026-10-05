# Sistema RAG (Streamlit + FastAPI + ChromaDB + Google AI)

Este proyecto implementa un sistema **RAG (Generación Aumentada por Recuperación)** completo y desacoplado, diseñado para responder preguntas sobre un corpus documental privado utilizando evidencia verificable, citas bibliográficas y un estricto control de abstención para evitar alucinaciones.

---

## 🏗️ Arquitectura del Sistema

El sistema se divide en dos capas principales que se comunican vía HTTP JSON:
1. **Frontend (Streamlit):** Interfaz gráfica de usuario en formato chat que permite subir documentos, consultar información, ver citas bibliográficas con scores y gestionar el historial local.
2. **Backend (FastAPI):** API REST que gestiona la partición de textos (*chunking*), la vectorización mediante **Google AI Studio**, la persistencia vectorial en **ChromaDB** y la generación de respuestas ancladas con **Gemini**.

## 🚀 Guía de Instalación y Configuración

### 1. Clonar o posicionarse en el proyecto
Abre tu terminal y navega hasta la carpeta del proyecto:
```bash
cd proyecto_final/rag-app
```
### 2. Crear y activar un entorno virtual
Es indispensable aislar las dependencias del proyecto:
En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
En Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias
Instala todas las librerías necesarias especificadas en el proyecto:
```bash
pip install -r requirements.txt
```

### 4. . Configurar las credenciales
1. Copia el archivo de ejemplo .env.example y nómbralo .env:
```bash
cp .env.example .env
```
(O simplemente crea un archivo plano llamado .env en la raíz de rag-app).

2. Abre el archivo .env e introduce tu clave de API de la siguiente manera (sin espacios ni comillas adicionales):
```bash
GOOGLE_API_KEY="tu_clave_real_de_google_aqui"
```

▶️ Cómo Levantar el Sistema
Para que la aplicación funcione, necesitarás dos terminales abiertas de manera simultánea (ambas con el entorno virtual venv activado).

Terminal 1: Iniciar el Backend (FastAPI)
Ejecuta el servidor Uvicorn para levantar la API:
```bash
uvicorn app.main:app --reload --port 8000
```
Terminal 2: Iniciar el Frontend (Streamlit)
Ejecuta la interfaz gráfica de usuario:
```bash
streamlit run ui/streamlit_app.py
```
Verificación: Se abrirá automáticamente una pestaña en tu navegador en http://localhost:8501.

🧪 Cómo Probar el Sistema (Casos de Uso)
Cargar Documentos:

En la barra lateral de Streamlit, sube al menos 5 documentos en formato .txt, .md o .pdf.

Haz clic en "Indexar Documento". Verás cuántos fragmentos (chunks) se guardaron y aparecerán listados en la barra lateral.

Consultar (RAG):

Escribe una pregunta en el chat sobre el contenido de tus documentos.

El sistema te devolverá una respuesta redactada en español, acompañada de un acordeón desplegable que muestra las citas exactas [n], el archivo de origen y la distancia matemática (score).

Prueba de Abstención (Anti-alucinación):

Realiza una pregunta sobre un tema que no aparezca en ninguno de tus documentos (por ejemplo, algo completamente ajeno al corpus).

El sistema detectará la falta de contexto y se abstendrá formalmente ("El sistema no encontró evidencia suficiente..."), cumpliendo con la regla de oro de no inventar información.

Persistencia:

Detén el servidor de FastAPI (Ctrl + C) y vuelve a encenderlo. Comprobarás que los documentos siguen indexados gracias a la persistencia local en la carpeta chroma/.
