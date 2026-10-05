import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Usaremos un modelo de texto para responder, no el de embeddings
GENERATION_MODEL = "gemini-3.5-flash-lite"

def generate_answer(question: str, context_chunks: list[str]) -> tuple[str, bool]:
    """
    Genera una respuesta usando Gemini basándose SOLAMENTE en los chunks proporcionados.
    Devuelve la respuesta y un booleano 'abstained' (True si no pudo responder).
    """
    # Si ChromaDB no devolvió nada útil
    if not context_chunks:
        return "No tengo evidencia suficiente para responder a esa pregunta.", True

    # 1. Preparar el contexto enumerado para que Gemini pueda citar [1], [2], etc.
    context_text = ""
    for i, chunk in enumerate(context_chunks):
        context_text += f"[{i+1}] {chunk}\n\n"

    # 2. El Prompt (Instrucciones estrictas para el modelo)
    prompt = f"""
Eres un asistente experto de un sistema RAG. Tu tarea es responder a la pregunta del usuario utilizando ÚNICAMENTE la información proporcionada en la sección "Evidencia Recuperada".

Reglas estrictas:
1. Responde en español.
2. Si la evidencia contiene la respuesta, redacta una respuesta clara y concisa.
3. Debes incluir citas usando el formato [n] al final de las oraciones para indicar de qué fragmento sacaste la información (ej. "Las mitocondrias producen energía [1]").
4. Si la "Evidencia Recuperada" NO contiene información suficiente para responder a la pregunta, DEBES responder exactamente con esta frase: "NO_HAY_EVIDENCIA" y no decir nada más. No uses tu conocimiento previo bajo ninguna circunstancia.

Evidencia Recuperada:
{context_text}

Pregunta: {question}
Respuesta:
"""

    # 3. Llamar a Gemini para generar texto
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt
    )
    
    answer_text = response.text.strip()
    
    # 4. Comprobar la abstención
    if "NO_HAY_EVIDENCIA" in answer_text:
        return "No tengo evidencia suficiente en los documentos proporcionados para responder a esa pregunta.", True
        
    return answer_text, False