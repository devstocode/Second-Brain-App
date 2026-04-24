import os


class Config:
    # Definimos dónde estará la base de datos de forma automática
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data", "db", "brain.db")

    # Nombre del modelo de IA que usaremos
    MODEL_NAME = 'all-MiniLM-L6-v2'