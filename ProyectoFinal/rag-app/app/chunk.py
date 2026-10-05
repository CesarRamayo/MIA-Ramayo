def get_chunks(text: str, chunk_size: int = 300, overlap: int = 50)-> list[str]:
    "Divide un texto largo en fragmentos más pequeños (chunks) basados en cantidad de palabras."

    #Separar el texto en una lista de palabras
    words = text.split()
    chunks = []

    if not words:
        return chunks

    i=0
    while i < len(words):
        #Tomar un bloque de palabras desde "i" hasta "i + chunk_size"
        chunk_words= words[i : i+ chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)

        #Avanzar el índice respetando el solape para que las últimas palabras se repitan en el siguiente chunk
        i += (chunk_size - overlap)
    return chunks