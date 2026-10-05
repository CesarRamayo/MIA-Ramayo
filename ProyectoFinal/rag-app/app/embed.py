import os
from dotenv import load_dotenv
from google import genai

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Inicializar el cliente de Gemini
client = genai.Client(api_key=api_key)

# Definir el modelo como una constante para no equivocarlo luego
EMBEDDING_MODEL = "gemini-embedding-001"

def get_embedding(text: str) -> list[float]:
    """
    Convierte un texto (chunk o pregunta) en un vector matemático usando Google AI.
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    # Devuelve la lista de números flotantes (el vector)
    return response.embeddings[0].values

def get_multiple_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Convierte una lista de textos en una lista de vectores. 
    (Útil para procesar varios chunks a la vez antes de subirlos a ChromaDB).
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts
    )
    # Extrae todos los vectores de la respuesta
    return [e.values for e in response.embeddings]