import numpy as np
from core.memory import DatabaseManager
from core.embeddings import TextEmbedder


class BrainService:
    def __init__(self):
        self.memoria = DatabaseManager()
        self.ia = TextEmbedder()

    def guardar_en_el_cerebro(self, texto, categoria):
        self.memoria.guardar(texto, categoria)
        print(f"🧠 Sistema: Conocimiento guardado en categoría '{categoria}'")

    def buscar_con_ia(self, consulta_usuario):
        """
        Busca en la memoria usando Inteligencia Artificial.
        """
        todos_los_apuntes = self.memoria.obtener_todos()

        if not todos_los_apuntes:
            return []

        # 1. Convertimos la búsqueda del usuario en un vector (números)
        vector_busqueda = self.ia.generar_embeddings(consulta_usuario)

        resultados = []

        for apunte in todos_los_apuntes:
            # apunte[1] es el texto del apunte
            texto_apunte = apunte[1]

            # 2. Convertimos el apunte guardado en vector
            vector_apunte = self.ia.generar_embeddings(texto_apunte)

            # 3. Calculamos la similitud (matemáticas vectoriales)
            # Esto devuelve un número entre 0 y 1 (qué tanto se parecen)
            similitud = np.dot(vector_busqueda, vector_apunte) / (
                        np.linalg.norm(vector_busqueda) * np.linalg.norm(vector_apunte))

            resultados.append({
                'id': apunte[0],
                'texto': texto_apunte,
                'categoria': apunte[2],
                'score': similitud
            })

        # 4. Ordenamos por los más parecidos (mayor score)
        resultados.sort(key=lambda x: x['score'], reverse=True)

        return resultados[:3]  # Devolvemos los 3 mejores resultados

    def eliminar_apunte(self, texto):
        """Recibe la orden de la interfaz y ordena a la BD que elimine el texto."""
        if texto:
            # Cambiamos 'bd' por 'memoria' para que coincida con tu inicialización
            self.memoria.eliminar_apunte(texto)
            return True
        return False