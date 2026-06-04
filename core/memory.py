import sqlite3
from app.config import Config

class DatabaseManager:
    def __init__(self):
        # Usamos la ruta que definimos en el archivo de configuración
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.cursor = self.conn.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        # Creamos la tabla si no existe (id, contenido del estudio, y categoría)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recuerdos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                categoria TEXT
            )
        ''')
        self.conn.commit()

    def guardar(self, texto, categoria="General"):
        self.cursor.execute('INSERT INTO recuerdos (contenido, categoria) VALUES (?, ?)', (texto, categoria))
        self.conn.commit()

    def obtener_todos(self):
        self.cursor.execute('SELECT * FROM recuerdos')
        return self.cursor.fetchall()

    def eliminar_apunte(self, contenido_texto):
        """Elimina un apunte de la base de datos buscando su contenido exacto."""
        # Ejecutamos el borrado en la tabla 'recuerdos' buscando en la columna 'contenido'
        self.cursor.execute("DELETE FROM recuerdos WHERE contenido = ?", (contenido_texto,))
        self.conn.commit()