# core/embeddings.py
from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self):
        # Cargamos un modelo de IA rápido y ligero ideal para textos
        self.modelo = SentenceTransformer('all-MiniLM-L6-v2')

    def generar_embeddings(self, texto):
        """
        Toma un texto normal y lo convierte en un vector de números (numpy array).
        Esta es la función que tu brain_service.py estaba buscando.
        """
        vector = self.modelo.encode(texto)
        return vector