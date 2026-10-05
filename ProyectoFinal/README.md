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
