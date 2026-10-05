from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uvicorn
import shutil
import os

# Importamos nuestros módulos construidos
from pypdf import PdfReader
from app.chunk import get_chunks
from app.embed import get_embedding, get_multiple_embeddings
from app.store import add_chunks_to_chroma, search_in_chroma
from app.generate import generate_answer

from app.store import add_chunks_to_chroma, search_in_chroma, get_all_documents, delete_document
from app.generate import generate_answer


app = FastAPI(title="Sistema RAG - Proyecto Final")

# Directorio temporal para guardar archivos antes de procesarlos
os.makedirs("data", exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    source_filter: str | None = None  # <-- Nuevo parámetro opcional

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API RAG lista y funcionando."}


# NUEVO ENDPOINT: Listar documentos
@app.get("/documents")
def list_documents():
    try:
        docs = get_all_documents()
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NUEVO ENDPOINT: Borrar documentos
@app.delete("/documents/{filename}")
def remove_document(filename: str):
    try:
        delete_document(filename)
        return {"message": f"Documento {filename} eliminado de la base de datos."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Recibe un documento, lo parte en chunks, lo convierte a embeddings 
    y lo guarda en ChromaDB.
    """
    try:
        # 1. Guardar el archivo localmente en la carpeta data
        file_path = f"data/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Lógica condicional para leer PDF o TX/MD
        text=""
        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            #Si es txt o md, lo leemos normal
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
        # 3. Partir en chunks
        chunks = get_chunks(text, chunk_size=200, overlap=50)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="El documento no contiene texto válido.")
            
        # 4. Generar embeddings
        embeddings = get_multiple_embeddings(chunks)

        delete_document(file.filename)
        add_chunks_to_chroma(chunks, embeddings, source_name=file.filename)
        
        # 5. Guardar en ChromaDB
        add_chunks_to_chroma(chunks, embeddings, source_name=file.filename)
        
        return {
            "message": "Documento indexado correctamente.",
            "filename": file.filename,
            "chunks_creados": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_rag(request: QueryRequest):
    """
    Recibe una pregunta, busca en la base vectorial, y genera una respuesta anclada.
    """
    try:
        # 1. Incrustar la pregunta
        query_vector = get_embedding(request.question)
        
        # 2. Recuperar evidencia (ahora le pasamos el filtro si existe)
        raw_results = search_in_chroma(query_vector, request.top_k, request.source_filter)
        
        # Extraer los datos de forma limpia
        context_chunks = raw_results['documents'][0] if raw_results['documents'] else []
        metadatas = raw_results['metadatas'][0] if raw_results['metadatas'] else []
        scores = raw_results['distances'][0] if raw_results['distances'] else []
        
        # Formatear las citas para el requisito del proyecto
        citations = []
        for i in range(len(context_chunks)):
            citations.append({
                "id": i + 1,
                "source": metadatas[i]['source'],
                "text": context_chunks[i],
                "score": scores[i]
            })
            
        # 3. Generar la respuesta usando Gemini
        answer, abstained = generate_answer(request.question, context_chunks)
        
        return {
            "answer": answer,
            "citations": citations,
            "abstained": abstained
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)