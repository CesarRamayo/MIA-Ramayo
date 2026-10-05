import chromadb
import uuid

# 1. Iniciar un cliente persistente (guardará los datos en la carpeta "chroma" de tu proyecto)
chroma_client = chromadb.PersistentClient(path="./chroma")

# 2. Crear o recuperar la colección de datos
collection = chroma_client.get_or_create_collection(name="documentos_rag")

def add_chunks_to_chroma(chunks: list[str], embeddings: list[list[float]], source_name: str):
    """
    Guarda los textos y sus vectores matemáticos en ChromaDB.
    """
    if not chunks:
        return
    
    # ChromaDB exige que cada pedazo de texto tenga un ID único
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    
    # Guardamos metadatos para saber de qué archivo vino cada pedazo (requisito de tu proyecto)
    metadatas = [{"source": source_name, "chunk_index": i} for i in range(len(chunks))]
    
    # ¡Agregamos todo! Fíjate que le pasamos 'embeddings' directamente
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)

def search_in_chroma(query_embedding: list[float], top_k: int = 3, source_filter: str = None):
    """
    Busca los fragmentos más similares. Si se pasa un source_filter, 
    busca SOLO dentro de ese archivo.
    """
    # Preparamos los argumentos básicos
    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }
    
    # Si el usuario eligió un archivo específico, agregamos el filtro 'where'
    if source_filter:
        query_args["where"] = {"source": source_filter}
        
    results = collection.query(**query_args)
    return results

def get_all_documents() -> list[str]:
    """
    Obtiene una lista de todos los documentos (sources) únicos indexados en ChromaDB.
    """
    # Obtenemos todos los metadatos de la colección
    results = collection.get(include=["metadatas"])
    
    # Usamos un 'set' (conjunto) para guardar solo los nombres únicos, sin repetir
    sources = set()
    for meta in results.get("metadatas", []):
        if meta and "source" in meta:
            sources.add(meta["source"])
            
    return list(sources)

def delete_document(source_name: str):
    """
    Borra todos los fragmentos (chunks) asociados a un documento específico.
    """
    # ChromaDB permite borrar registros filtrando por metadatos
    collection.delete(where={"source": source_name})